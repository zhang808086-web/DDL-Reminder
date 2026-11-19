"""Asynchronous, notification-only GitHub release checks."""

import json
import time

from packaging.version import Version
from PySide6.QtCore import QObject, Property, QSettings, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from ddl_reminder.version import APP_VERSION


REPOSITORY = "zhang808086-web/DDL-Reminder"
RELEASES_URL = f"https://github.com/{REPOSITORY}/releases"


class UpdateController(QObject):
    stateChanged = Signal()
    updateAvailable = Signal(str)

    def __init__(self, parent: QObject | None = None, *, network=None, settings=None):
        super().__init__(parent)
        self._network = network if network is not None else QNetworkAccessManager(self)
        self._settings = settings if settings is not None else QSettings("DDL-Reminder", "Updates")
        self._reply = None
        self._status = "可检查是否有新版本"
        self._latest = ""
        self._release_url = ""
        self._download_url = ""
        self._closed = False
        self._auto_timer = QTimer(self)
        self._auto_timer.setInterval(3_600_000)
        self._auto_timer.timeout.connect(self.checkAutomatically)
        self._auto_timer.start()

    @Property(str, constant=True)
    def currentVersion(self):
        return APP_VERSION

    @Property(bool, notify=stateChanged)
    def checking(self):
        return self._reply is not None

    @Property(str, notify=stateChanged)
    def status(self):
        return self._status

    @Property(str, notify=stateChanged)
    def latestVersion(self):
        return self._latest

    @Property(bool, notify=stateChanged)
    def hasUpdate(self):
        return bool(self._release_url)

    @Slot()
    def checkAutomatically(self):
        try:
            last = float(self._settings.value("lastSuccessfulCheck", 0))
        except (TypeError, ValueError):
            last = 0
        elapsed = time.time() - last
        if elapsed < 0 or elapsed >= 86400:
            self.checkNow()

    @Slot()
    def checkNow(self):
        if self.checking or self._closed:
            return
        request = QNetworkRequest(QUrl(
            f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
        ))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", f"DDL-Reminder/{APP_VERSION}".encode())
        request.setTransferTimeout(15000)
        self._status = "正在检查更新…"
        reply = self._network.get(request)
        self._reply = reply
        reply.downloadProgress.connect(
            lambda received, total: reply.abort() if max(received, total) > 2_000_000 else None
        )
        reply.finished.connect(self._finished)
        self.stateChanged.emit()

    def _finished(self):
        reply = self._reply
        self._reply = None
        available = False
        try:
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if status == 404:
                self._status = "暂无可用的正式版本"
                return
            if reply.error() != QNetworkReply.NetworkError.NoError or status != 200:
                self._status = "暂时无法检查更新，请稍后重试"
                return
            data = json.loads(bytes(reply.readAll()))
            latest = Version(data["tag_name"].removeprefix("v"))
            if data.get("draft") or data.get("prerelease") or latest.is_prerelease or latest.is_devrelease:
                raise ValueError("Not a stable release")
            self._latest = str(latest)
            self._release_url = ""
            self._download_url = ""
            if latest > Version(APP_VERSION):
                release_url = data.get("html_url", "")
                if not release_url.startswith(RELEASES_URL + "/tag/"):
                    raise ValueError("Unexpected release URL")
                self._release_url = release_url
                expected = f"DDL-Reminder-Setup-v{latest}.exe"
                for asset in data.get("assets", []):
                    url = asset.get("browser_download_url", "")
                    if asset.get("name") == expected and url.startswith(RELEASES_URL + "/download/"):
                        self._download_url = url
                        break
                self._status = f"发现新版本 {latest}"
                available = True
            else:
                self._status = f"当前已是最新版本（{APP_VERSION}）"
            self._settings.setValue("lastSuccessfulCheck", time.time())
        except (ValueError, KeyError, TypeError, AttributeError):
            self._status = "更新信息无效，请稍后重试"
            self._release_url = ""
            self._download_url = ""
        finally:
            reply.deleteLater()
            self.stateChanged.emit()
            if available:
                self.updateAvailable.emit(self._latest)

    @Slot(result=bool)
    def openDownload(self):
        url = self._download_url or self._release_url
        return bool(url) and QDesktopServices.openUrl(QUrl(url))

    def shutdown(self):
        self._closed = True
        self._auto_timer.stop()
        if self._reply is not None:
            self._reply.abort()
