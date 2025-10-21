#!/usr/bin/env python3
"""
Material Design 3 Demo with PySide6 QML
Demostración completa de Material Design 3 con Qt Quick Controls
"""

import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QObject, Slot, Property, Signal, QTimer
from PySide6.QtQuickControls2 import QQuickStyle

class MaterialThemeController(QObject):
    """Controlador para temas y estilos Material Design 3"""

    themeChanged = Signal()
    primaryColorChanged = Signal()
    darkModeChanged = Signal()

    def __init__(self):
        super().__init__()
        self._dark_mode = False
        self._primary_color = "#6750A4"  # Material 3 Purple
        self._available_colors = {
            "Material 3 Purple": "#6750A4",
            "Material 3 Blue": "#0061A4",
            "Material 3 Green": "#146C2E",
            "Material 3 Orange": "#7D5700",
            "Material 3 Red": "#BA1A1A"
        }

    @Property(bool, notify=darkModeChanged)
    def darkMode(self):
        return self._dark_mode

    @darkMode.setter
    def darkMode(self, value):
        if self._dark_mode != value:
            self._dark_mode = value
            self.darkModeChanged.emit()
            self.themeChanged.emit()

    @Property(str, notify=primaryColorChanged)
    def primaryColor(self):
        return self._primary_color

    @primaryColor.setter
    def primaryColor(self, color):
        if self._primary_color != color:
            self._primary_color = color
            self.primaryColorChanged.emit()
            self.themeChanged.emit()

    @Slot(str)
    def setPrimaryColorByName(self, color_name):
        """Establece el color primario por nombre"""
        if color_name in self._available_colors:
            self.primaryColor = self._available_colors[color_name]

    @Slot()
    def toggleDarkMode(self):
        """Cambia entre modo claro y oscuro"""
        self.darkMode = not self.darkMode

    @Slot(result="QStringList")
    def getAvailableColors(self):
        """Devuelve la lista de colores disponibles"""
        return list(self._available_colors.keys())

class MaterialDataModel(QObject):
    """Modelo de datos para demostración"""

    dataChanged = Signal()

    def __init__(self):
        super().__init__()
        self._tasks = [
            {"title": "Review Material Design Guidelines", "completed": True, "priority": "High"},
            {"title": "Implement Dynamic Theme", "completed": False, "priority": "Medium"},
            {"title": "Add Custom Components", "completed": False, "priority": "Low"},
            {"title": "Test Dark Mode", "completed": True, "priority": "High"},
            {"title": "Optimize Performance", "completed": False, "priority": "Medium"}
        ]
        self._stats = {
            "total_tasks": len(self._tasks),
            "completed_tasks": sum(1 for task in self._tasks if task["completed"]),
            "high_priority": sum(1 for task in self._tasks if task["priority"] == "High")
        }

    @Property("QVariantList", notify=dataChanged)
    def tasks(self):
        return self._tasks

    @Property("QVariantMap", notify=dataChanged)
    def stats(self):
        return self._stats

    @Slot(int, bool)
    def toggleTaskCompletion(self, index, completed):
        """Cambia el estado de completado de una tarea"""
        if 0 <= index < len(self._tasks):
            self._tasks[index]["completed"] = completed
            self._update_stats()
            self.dataChanged.emit()

    @Slot(str)
    def addTask(self, title):
        """Agrega una nueva tarea"""
        new_task = {
            "title": title,
            "completed": False,
            "priority": "Medium"
        }
        self._tasks.append(new_task)
        self._update_stats()
        self.dataChanged.emit()

    def _update_stats(self):
        """Actualiza las estadísticas"""
        self._stats = {
            "total_tasks": len(self._tasks),
            "completed_tasks": sum(1 for task in self._tasks if task["completed"]),
            "high_priority": sum(1 for task in self._tasks if task["priority"] == "High")
        }

def create_material_qml_file():
    """Crea el archivo QML con Material Design 3"""

    qml_content = '''
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Effects

ApplicationWindow {
    id: window
    width: 1200
    height: 800
    visible: true
    title: "Material Design 3 Demo - PySide6"

    // Material Design 3 Configuration
    Material.theme: themeController.darkMode ? Material.Dark : Material.Light
    Material.primary: themeController.primaryColor
    Material.accent: themeController.primaryColor
    Material.background: Material.theme === Material.Light ? "#FFFBFE" : "#1C1B1F"
    Material.foreground: Material.theme === Material.Light ? "#1C1B1F" : "#E6E1E5"

    // Property animations
    Behavior on Material.primary {
        ColorAnimation { duration: 300; easing.type: Easing.InOutQuad }
    }

    // Theme Controller
    property alias themeController: themeController

    ThemeController {
        id: themeController
    }

    // Data Model
    property alias dataModel: dataModel

    MaterialDataModel {
        id: dataModel
    }

    // Main Content
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 24

        // Header
        RowLayout {
            Layout.fillWidth: true

            Label {
                text: "Material Design 3"
                font.pixelSize: 32
                font.weight: 700
                Material.foreground: Material.primary
                Layout.alignment: Qt.AlignLeft
            }

            Item { Layout.fillWidth: true }

            // Theme Controls
            Row {
                spacing: 12
                Layout.alignment: Qt.AlignRight

                ComboBox {
                    id: colorCombo
                    model: themeController.getAvailableColors()
                    currentIndex: 0
                    onCurrentValueChanged: {
                        themeController.setPrimaryColorByName(currentValue)
                    }

                    Material.roundedScale: Material.FullScale
                }

                Button {
                    text: themeController.darkMode ? "☀️ Light" : "🌙 Dark"
                    onClicked: themeController.toggleDarkMode()

                    Material.roundedScale: Material.FullScale

                    background: Rectangle {
                        color: themeController.darkMode ? Material.color(Material.Yellow, Material.Shade800) : Material.color(Material.Blue, Material.Shade600)
                        radius: 20
                        implicitWidth: 120
                        implicitHeight: 40

                        Behavior on color {
                            ColorAnimation { duration: 300 }
                        }
                    }
                }
            }
        }

        // Stats Cards
        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            Repeater {
                model: [
                    { title: "Total Tasks", value: dataModel.stats.total_tasks, color: Material.primary },
                    { title: "Completed", value: dataModel.stats.completed_tasks, color: Material.color(Material.Green) },
                    { title: "High Priority", value: dataModel.stats.high_priority, color: Material.color(Material.Red) }
                ]

                delegate: Card {
                    Layout.preferredWidth: 200
                    Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8

                        Label {
                            text: modelData.title
                            font.pixelSize: 14
                            Material.foreground: Material.color(Material.Grey)
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Label {
                            text: modelData.value
                            font.pixelSize: 28
                            font.weight: 700
                            Material.foreground: modelData.color
                            Layout.alignment: Qt.AlignHCenter
                        }
                    }
                }
            }
        }

        // Main Content Area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 24

            // Task List
            Card {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    Label {
                        text: "Tasks"
                        font.pixelSize: 20
                        font.weight: 600
                        Layout.alignment: Qt.AlignLeft
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        ColumnLayout {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: dataModel.tasks

                                delegate: TaskItem {
                                    title: modelData.title
                                    completed: modelData.completed
                                    priority: modelData.priority
                                    onToggled: function(completed) {
                                        dataModel.toggleTaskCompletion(index, completed)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Action Panel
            Card {
                Layout.preferredWidth: 300
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    Label {
                        text: "Quick Actions"
                        font.pixelSize: 18
                        font.weight: 600
                    }

                    TextField {
                        id: newTaskField
                        placeholderText: "New task..."
                        Layout.fillWidth: true

                        Material.roundedScale: Material.MediumScale
                    }

                    Button {
                        text: "Add Task"
                        Layout.fillWidth: true
                        onClicked: {
                            if (newTaskField.text.trim()) {
                                dataModel.addTask(newTaskField.text.trim())
                                newTaskField.text = ""
                            }
                        }

                        Material.roundedScale: Material.MediumScale
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: Material.color(Material.Grey, Material.Shade300)
                    }

                    // Material 3 Buttons
                    ColumnLayout {
                        spacing: 12

                        Button {
                            text: "Filled Button"
                            Layout.fillWidth: true
                            highlighted: true

                            Material.roundedScale: Material.FullScale
                        }

                        Button {
                            text: "Tonal Button"
                            Layout.fillWidth: true
                            flat: true

                            background: Rectangle {
                                color: Material.secondaryContainerColor
                                radius: 20
                                implicitWidth: 200
                                implicitHeight: 40

                                Behavior on color {
                                    ColorAnimation { duration: 200 }
                                }
                            }

                            Material.roundedScale: Material.FullScale
                        }

                            Button {
                            text: "Outlined Button"
                            Layout.fillWidth: true
                            flat: true

                            background: Rectangle {
                                color: "transparent"
                                border.color: Material.outlineColor
                                border.width: 1
                                radius: 20
                                implicitWidth: 200
                                implicitHeight: 40

                                Behavior on border.color {
                                    ColorAnimation { duration: 200 }
                                }
                            }

                            Material.roundedScale: Material.FullScale
                        }

                        TextButton {
                            text: "Text Button"
                            Layout.fillWidth: true

                            Material.roundedScale: Material.FullScale
                        }
                    }
                }
            }
        }
    }

    // Custom Components
    component Card: Rectangle {
        id: card

        property alias content: contentLoader.sourceComponent

        color: Material.theme === Material.Light ? Material.color(Material.Grey, Material.Shade100) : Material.color(Material.Grey, Material.Shade900)
        radius: 16

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowBlur: 0.6
            shadowColor: "black"
            shadowOpacity: 0.2
            shadowVerticalOffset: 2
            shadowHorizontalOffset: 1
        }

        Loader {
            id: contentLoader
            anchors.fill: parent
        }
    }

    component TaskItem: Rectangle {
        property alias title: titleLabel.text
        property alias completed: check.checked
        property string priority
        signal toggled(bool completed)

        id: taskItem

        height: 64
        color: completed ? Material.color(Material.Primary, Material.Shade100) : Material.containerColor
        radius: 12
        border.width: 1
        border.color: Material.outlineColor

        Behavior on color {
            ColorAnimation { duration: 300 }
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            CheckBox {
                id: check
                onClicked: taskItem.toggled(checked)
                Material.roundedScale: Material.MediumScale
            }

            Label {
                id: titleLabel
                Layout.fillWidth: true
                font.pixelSize: 16
                Material.foreground: completed ? Material.color(Material.Primary) : Material.foreground
            }

            Label {
                text: priority
                font.pixelSize: 12
                font.weight: 600
                padding: 4
                background: Rectangle {
                    color: priority === "High" ? Material.color(Material.Red, Material.Shade100) :
                           priority === "Medium" ? Material.color(Material.Orange, Material.Shade100) :
                           Material.color(Material.Blue, Material.Shade100)
                    radius: 4
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: check.checked = !check.checked
        }
    }
}
'''

    return qml_content

def main():
    """Función principal de la demostración"""

    # Configurar el estilo de Qt Quick Controls
    QQuickStyle.setStyle("Material")

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("Material Design Demo")
    app.setApplicationName("PySide6 Material Design 3")

    # Crear el archivo QML dinámicamente
    qml_content = create_material_qml_file()

    # Crear la aplicación QML
    engine = QQmlApplicationEngine()

    # Registrar los tipos personalizados
    qmlRegisterType(MaterialThemeController, "MaterialDemo", 1, 0, "ThemeController")
    qmlRegisterType(MaterialDataModel, "MaterialDemo", 1, 0, "MaterialDataModel")

    # Cargar el contenido QML directamente
    engine.loadData(qml_content.encode('utf-8'), QUrl())

    if not engine.rootObjects():
        print("Error: Failed to load QML content")
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()