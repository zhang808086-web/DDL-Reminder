import json
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QApplication

from ddl_reminder.ui.update_controller import UpdateController, RELEASES_URL


class MemorySettings:
    def __init__(self):
        self.values = {}

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


class Reply(QObject):
    finished = Signal()
    downloadProgress = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.code = 200
        self.payload = b""
        self.network_error = QNetworkReply.NetworkError.NoError

    def attribute(self, _key):
        return self.code

    def error(self):
        return self.network_error

    def readAll(self):
        return self.payload

    def abort(self):
        self.network_error = QNetworkReply.NetworkError.OperationCanceledError
        self.finished.emit()


class Network:
    def __init__(self):
        self.calls = []
        self.reply = Reply()

    def get(self, request):
        self.calls.append(request)
        self.reply = Reply()
        return self.reply


@pytest.fixture
def updater():
    app = QApplication.instance() or QApplication([])
    network = Network()
    settings = MemorySettings()
    controller = UpdateController(network=network, settings=settings)
    yield controller, network, settings
    controller.shutdown()
    app.processEvents()


def release(tag="v999.0.0", **kwargs):
    return {
        "tag_name": tag, "draft": False, "prerelease": False,
        "html_url": RELEASES_URL + "/tag/" + tag,
        "assets": [{"name": "DDL-Reminder-Setup-v999.0.0.exe",
                    "browser_download_url": RELEASES_URL + "/download/" + tag + "/setup.exe"}],
        **kwargs,
    }


def respond(controller, network, payload):
    controller.checkNow()
    network.reply.payload = json.dumps(payload).encode()
    network.reply.finished.emit()


def test_new_release_notifies_once_and_opens_trusted_asset(updater, monkeypatch):
    controller, network, settings = updater
    notices, urls = [], []
    controller.updateAvailable.connect(notices.append)
    monkeypatch.setattr("ddl_reminder.ui.update_controller.QDesktopServices.openUrl",
                        lambda url: urls.append(url.toString()) or True)
    respond(controller, network, release())
    assert notices == ["999.0.0"]
    assert controller.hasUpdate and controller.openDownload()
    assert urls == [RELEASES_URL + "/download/v999.0.0/setup.exe"]
    assert settings.value("lastSuccessfulCheck") > 0
    controller.checkAutomatically()
    assert len(network.calls) == 1


@pytest.mark.parametrize("payload", [
    {}, [], release(tag="nonsense"), release(prerelease=True), release(draft=True),
    release(tag="v999.0.0rc1"), release(html_url="https://evil.example/setup.exe"),
])
def test_invalid_or_untrusted_release_cannot_offer_download(updater, payload):
    controller, network, settings = updater
    respond(controller, network, payload)
    assert not controller.hasUpdate
    assert not controller.openDownload()
    assert settings.value("lastSuccessfulCheck") is None


def test_older_release_and_missing_asset_fallback(updater):
    controller, network, _ = updater
    respond(controller, network, release(tag="v0.1.0"))
    assert not controller.hasUpdate
    respond(controller, network, release(assets=[]))
    assert controller.hasUpdate
    assert controller._download_url == ""
    assert controller._release_url == RELEASES_URL + "/tag/v999.0.0"


def test_request_failure_allows_retry_and_shutdown_cancels(updater):
    controller, network, settings = updater
    controller.checkNow()
    controller.checkNow()
    assert len(network.calls) == 1
    network.reply.network_error = QNetworkReply.NetworkError.TimeoutError
    network.reply.finished.emit()
    assert not controller.checking
    assert settings.value("lastSuccessfulCheck") is None
    controller.checkNow()
    controller.shutdown()
    assert not controller.checking
    controller.checkNow()
    assert len(network.calls) == 2


def test_automatic_check_obeys_interval_but_manual_check_does_not(updater):
    controller, network, settings = updater
    settings.setValue("lastSuccessfulCheck", time.time())
    controller.checkAutomatically()
    assert not network.calls
    controller.checkNow()
    assert len(network.calls) == 1
