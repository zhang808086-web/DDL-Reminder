import QtQuick
import ".." as App

Rectangle {
    id: chip
    property string category: "normal"
    property string label: ""
    readonly property color tone: category === "overdue" ? App.Theme.danger
                                  : category === "within_one_hour" ? "#FF8E66"
                                  : category === "within_one_day" ? App.Theme.warning
                                  : App.Theme.cyan
    implicitWidth: chipText.implicitWidth + 20
    implicitHeight: 27
    radius: 14
    color: Qt.rgba(tone.r, tone.g, tone.b, 0.13)
    border.color: Qt.rgba(tone.r, tone.g, tone.b, 0.35)

    Text {
        id: chipText
        anchors.centerIn: parent
        text: chip.label
        color: chip.tone
        font.family: App.Theme.fontFamily
        font.pixelSize: 12
        font.weight: Font.DemiBold
    }
}
