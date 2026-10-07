import QtQuick
import QtQuick.Layouts

RowLayout {
    id: fields
    property alias dateText: dateField.text
    property alias timeText: timeField.text
    spacing: 12

    FormField {
        id: dateField
        Layout.fillWidth: true
        label: "截止日期"
        placeholderText: "YYYY-MM-DD"
        maximumLength: 10
    }
    FormField {
        id: timeField
        Layout.preferredWidth: 150
        label: "时间"
        placeholderText: "HH:MM"
        maximumLength: 5
    }
}
