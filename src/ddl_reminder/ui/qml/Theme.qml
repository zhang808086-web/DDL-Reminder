pragma Singleton
import QtQuick

QtObject {
    readonly property color canvas: "#070B17"
    readonly property color surface: "#0D1426"
    readonly property color surfaceRaised: "#121C32"
    readonly property color surfaceHover: "#182542"
    readonly property color border: "#263653"
    readonly property color borderSoft: "#192742"
    readonly property color textPrimary: "#F4F7FF"
    readonly property color textSecondary: "#9AA9C3"
    readonly property color textMuted: "#63718B"
    readonly property color cyan: "#42D7FF"
    readonly property color cyanDim: "#163A50"
    readonly property color violet: "#8A7CFF"
    readonly property color success: "#4FD1A1"
    readonly property color warning: "#F3B75B"
    readonly property color danger: "#FF6B7A"

    readonly property int radiusSmall: 8
    readonly property int radiusMedium: 12
    readonly property int radiusLarge: 18
    readonly property int radiusPanel: 24
    readonly property int spacingSmall: 8
    readonly property int spacingMedium: 14
    readonly property int spacingLarge: 22
    readonly property string fontFamily: "Microsoft YaHei UI"
}
