import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

pragma Singleton

ApplicationWindow {
    id: window
    width: 960
    height: 640
    color: "#11121b"
    title: qsTr("Modern QML Dashboard")
    visible: true

    FontLoader {
        id: interFont
        source: "https://fonts.gstatic.com/s/inter/v12/UcC73FwrK5A4Sg_tZylOCw.ttf"
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#191b2a" }
            GradientStop { position: 1.0; color: "#0c0d13" }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 20

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true

                Text {
                    text: "Panel Inteligente"
                    color: "#ffffff"
                    font.pointSize: 24
                    font.family: interFont.name
                    font.bold: true
                }
                Text {
                    text: "Resumen de actividad de RAG y transcripciones"
                    color: "#8fa0d6"
                    font.pointSize: 14
                    font.family: interFont.name
                }
            }

            Button {
                text: "Sincronizar"
                font.family: interFont.name
                font.bold: true
                palette.button: "#4b6ef5"
                palette.buttonText: "#ffffff"
                contentItem: Text {
                    text: control.text
                    font: control.font
                    color: control.palette.buttonText
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    implicitWidth: 140
                    implicitHeight: 40
                    color: control.down ? "#2d4ade" : "#4b6ef5"
                    radius: 20
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 18

            Repeater {
                model: [
                    { "title": "Videos procesados", "value": "128", "caption": "vs. día anterior", "trend": "+24%" },
                    { "title": "Resúmenes generados", "value": "64", "caption": "Tasa de éxito", "trend": "92%" },
                    { "title": "Consultas RAG", "value": "483", "caption": "Tiempo medio respuesta", "trend": "1.4s" }
                ]

                delegate: Rectangle {
                    radius: 18
                    color: "#1b1d2a"
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    Layout.minimumHeight: 140
                    border.color: "#2a2d3c"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 10

                        Text {
                            text: modelData.title
                            color: "#8fa0d6"
                            font.pointSize: 13
                            font.family: interFont.name
                        }

                        Text {
                            text: modelData.value
                            color: "#fafbff"
                            font.pointSize: 32
                            font.family: interFont.name
                            font.bold: true
                        }

                        RowLayout {
                            spacing: 6
                            Text {
                                text: modelData.caption
                                color: "#6e7fb6"
                                font.pointSize: 12
                                font.family: interFont.name
                            }
                            Text {
                                text: modelData.trend
                                color: "#58d6a6"
                                font.pointSize: 12
                                font.family: interFont.name
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 18
            color: "#1b1d2a"
            border.color: "#2a2d3c"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                RowLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "Actividad reciente"
                        color: "#ffffff"
                        font.pointSize: 18
                        font.family: interFont.name
                        font.bold: true
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: "Ver todo"
                        color: "#4b6ef5"
                        font.pointSize: 14
                        font.family: interFont.name
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: 10
                    model: [
                        { time: "10:24", text: "Ingestado \"TensorFlow Agents\"" },
                        { time: "10:12", text: "Resumen \"Curso LangChain\" (Gemini)" },
                        { time: "09:58", text: "Consulta RAG: mejores prompts visión" },
                        { time: "09:41", text: "Eliminado vídeo duplicado" },
                        { time: "09:12", text: "Ingestado \"PySide6 modern UI\"" }
                    ]

                    delegate: Rectangle {
                        width: parent.width
                        radius: 14
                        height: 64
                        color: hovered ? "#24273c" : "#1e2030"
                        border.color: hovered ? "#4b6ef5" : "#26293a"
                        border.width: 1

                        property bool hovered: false

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: parent.hovered = true
                            onExited: parent.hovered = false
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 16

                            Rectangle {
                                width: 36
                                height: 36
                                radius: 12
                                color: "#30324a"
                                Text {
                                    anchors.centerIn: parent
                                    text: model.time
                                    color: "#9eaede"
                                    font.pointSize: 11
                                    font.family: interFont.name
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true

                                Text {
                                    text: model.text
                                    color: "#dce5ff"
                                    font.pointSize: 14
                                    font.family: interFont.name
                                }
                                Text {
                                    text: "Origen automático · Base de datos sincronizada"
                                    color: "#6e7fb6"
                                    font.pointSize: 11
                                    font.family: interFont.name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
