import QtQuick
import QtCharts
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Controls.Material

ApplicationWindow {
    id: mainWindow
    width: 1200
    height: 700
    minimumWidth: 1200
    minimumHeight: 700
    visible: true
    title: qsTr("QOscope")

    Material.theme: Material.Dark
    Material.accent: Material.Green

    RowLayout {
        id: mainLayout
        anchors.fill: parent
        spacing: -20

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"

            ChartView {
                id: chartView
                anchors.fill: parent
                antialiasing: true
                backgroundColor: "#303030"
                legend.visible: false
                animationOptions: ChartView.NoAnimation
                backgroundRoundness: 0

                property color titleColor: "white"

                Timer {
                   id: plotRefresh
                   interval: 1 / 60 * 1000 // 60 Hz
                   running: bridge.acquisition_state
                   repeat: true
                   onTriggered: {
                       bridge.update_plot(lineSeries)
                   }
               }

                ValuesAxis {
                    id: axisX
                    titleText: "Time (s)"
                    labelsVisible: true
                    labelsColor: "white"
                    labelsFont: mainWindow.font
                    color: "transparent"
                    titleBrush: chartView.titleColor
                    titleFont: mainWindow.font
                    min: 0
                    max: 0.2
                }

                ValuesAxis {
                    id: axisY
                    titleText: "Voltage (V)"
                    labelsVisible: true
                    labelsColor: "white"
                    labelsFont: mainWindow.font
                    color: "transparent"
                    titleBrush: chartView.titleColor
                    titleFont: mainWindow.font
                    min: 0
                    max: 5
                }

                LineSeries {
                    id: lineSeries
                    name: "signal1"
                    visible: true
                    color: "#3fea54"
                    axisX: axisX
                    axisY: axisY
                    pointsVisible: false
                }

                Component.onCompleted: {
                    bridge.expose_axes(axisX, axisY)
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.maximumWidth: 200
            Layout.bottomMargin: 75
            Layout.topMargin: 35
            Layout.rightMargin: 20
            color: "transparent"

            ColumnLayout {
                id: menuLayout
                anchors.fill: parent
                spacing: 15

                GroupBox {
                    title: qsTr("Timebase")
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        Text {
                            Layout.fillWidth: true
                            text: "time/div (1 div = 1/10 graph"
                            color: "white"
                        }

                        ComboBox {
                            id: timebaseBox
                            enabled: bridge.connection
                            Layout.fillWidth: true
                            model: [
                                "100 us",
                                "200 us",
                                "500 us",
                                "1 ms",
                                "2 ms",
                                "5 ms",
                                "10 ms",
                                "20 ms",
                            ]
                            currentIndex: 7
                            onActivated: bridge.set_timebase(timebaseBox.currentValue)
                        }
                    }
                }

                GroupBox {
                    Layout.fillWidth: true
                    Layout.topMargin: 30

                    label: Rectangle {
                        anchors.bottom: parent.top
                        anchors.bottomMargin: 40
                        CheckBox {
                            id: triggerCheck
                            enabled: bridge.connection
                            checked: false
                            text: qsTr("Trigger")
                            onClicked: bridge.set_trigger_state(triggerCheck.checked)
                        }
                    }

                    ComboBox {
                        id: triggerBox
                        enabled: bridge.connection
                        anchors.fill: parent
                        model: ["Rising", "Falling", "Any"]
                        onActivated: bridge.set_trigger_slope(triggerBox.currentValue)
                    }
                }

                GroupBox {
                    title: qsTr("Acquisition")
                    Layout.fillWidth: true

                    RowLayout {
                        anchors.fill: parent
                        Button {
                            id: runBtn
                            Layout.fillWidth: true
                            text: bridge.acquisition_state ? qsTr("Stop") : qsTr("Run")
                            onClicked: if (!bridge.connection) {
                                dialogBox.title = "Device not connected"
                                dialogText.text = "No device is connected. Connect a device first."
                                dialogBox.open()
                            } else {
                                bridge.clear_plot(lineSeries)
                                bridge.on_run_stop_button()
                            }
                        }

                        Button {
                            Layout.fillWidth: true
                            text: qsTr("Single")
                            enabled: !bridge.acquisition_state
                            onClicked: if (!bridge.connection) {
                                dialogBox.title = "Device not connected"
                                dialogText.text = "No device is connected. Connect a device first."
                                dialogBox.open()
                            } else {
                                bridge.on_single_button()
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("Stats")
                    Layout.fillWidth: true

                    Text {
                        text: qsTr("Refresh rate: ") + bridge.qfps.toFixed(2)
                        color: "white"
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }

                GroupBox {
                    id: groupDevice
                    title: qsTr("Device")
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing:0

                        RowLayout {
                            Button {
                                Layout.fillWidth: true
                                text: qsTr("Refresh")
                                onClicked: {
                                    portsList.model = bridge.get_ports()
                                }
                            }

                            Button {
                                Layout.fillWidth: true
                                text: bridge.connection ? qsTr("Disconnect") : qsTr("Connect")
                                onClicked: {
                                    if (!bridge.connection) {
                                        if(!bridge.connect_to_device(portsList.currentValue)) {
                                            dialogBox.title = "Connection failed"
                                            dialogText.text = "Could not connect to device. No port is selected or available. Refresh and try again."
                                            dialogBox.open()
                                        }
                                    } else {
                                        bridge.disconnect_from_device()
                                    }
                                }
                            }
                        }

                        ComboBox {
                            id: portsList
                            Layout.fillWidth: true
                            model: bridge.ports
                        }
                    }
                }
            }
        }

        Dialog {
            id: dialogBox
            property string msgTitle: ""
            property string msgText: ""
            anchors.centerIn: mainLayout
            standardButtons: Dialog.Cancel
            Material.accent: Material.LightGreen
            width: 350
            modal: true

            Text {
                id: dialogText
                height: parent.height
                width: parent.width
                color: "white"
                font.pointSize: 10
                wrapMode: Text.WordWrap
            }
        }
    }
}