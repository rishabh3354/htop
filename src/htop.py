import sys
import webbrowser
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSettings, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.QtGui import QDesktopServices
from htop_threads import DummyDataThread, CpuThread, RamThread, NetSpeedThread
from ui_splash_screen import Ui_SplashScreen
from style import theme_1
from ui_main import Ui_MainWindow
from utility import UtilsInfo

# GLOBALS
PRODUCT_NAME = "HTOP"
FREQUENCY_MAPPER = {1: 0.2, 2: 0.4, 3: 0.6, 4: 1, 5: 2, 6: 3}
counter = 0
jumper = 10


class MainWindow(QMainWindow):
    def __init__(self):
        from ui_functions import UIFunctions
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        UIFunctions.uiDefinitions(self)
        self.settings = QSettings("warlordsoft", "htop")
        self.net_frequency = 1
        self.cpu_frequency = 1
        self.ram_frequency = 1
        self.theme_selected = 1
        self.speed_unit = "MB/s | KB/s | B/s"
        self.temp_unit = "°C  (Celsius)"
        self.default_frequency()
        self.load_settings()
        self.ui.stackedWidget.setCurrentIndex(0)

        self.theme_selected = 1
        self.ui.drop_shadow_frame.setStyleSheet(theme_1)
        self.ui.page_credits.setStyleSheet(theme_1)
        self.ui.account_page.setStyleSheet(theme_1)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # home buttons
        self.ui.home_button_2.clicked.connect(self.credit_button_clicked)
        self.ui.monitor_button.clicked.connect(self.monitor_button_clicked)
        self.ui.setting_button.clicked.connect(self.setting_button_clicked)
        self.ui.account_button.clicked.connect(self.account_button_clicked)
        self.ui.speed.clicked.connect(self.monitor_button_clicked)
        self.ui.setting.clicked.connect(self.setting_button_clicked)
        self.ui.account.clicked.connect(self.account_button_clicked)

        # App setting buttons
        self.ui.horizontalSlider.valueChanged.connect(self.change_frequency_net)
        self.ui.horizontalSlider_2.valueChanged.connect(self.change_frequency_cpu)
        self.ui.horizontalSlider_3.valueChanged.connect(self.change_frequency_ram)
        self.ui.comboBox_2.currentIndexChanged.connect(self.change_net_speed_unit)
        self.ui.comboBox_3.currentIndexChanged.connect(self.change_temp_unit)
        # theme setup

        self.count = 1  # theme set counter
        self.setWindowFlags(Qt.FramelessWindowHint)

        def moveWindow(event):
            # RESTORE BEFORE MOVE
            if UIFunctions.returnStatus() == 1:
                UIFunctions.maximize_restore(self)

            # IF LEFT CLICK MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.ui.title_bar.mouseMoveEvent = moveWindow

        # signal and slots
        self.ui.warlordsoft_button.clicked.connect(self.redirect_to_warlordsoft)
        self.ui.donate_button.clicked.connect(self.redirect_to_paypal_donation)
        self.ui.rate_button.clicked.connect(self.redirect_to_rate_snapstore)
        self.ui.feedback_button.clicked.connect(self.redirect_to_feedback_button)

        #  ======================Your plan functionality end=============================================

        self.load_cpu_data()
        self.load_ram_data()
        self.load_net_speed_data()
        self.show()
        self.load_annimation_data()

    def setValue(self, sliderValue, labelPercentage, progressBarName, color, net_value=50, net=False):
        if net:
            htmlText = """<p align="center"><span style=" font-size:50pt;">{VALUE}</span><span style=" font-size:40pt; vertical-align:super;"></span></p>"""
        else:
            htmlText = """<p align="center"><span style=" font-size:30pt;">{VALUE}</span><span style=" font-size:20pt; vertical-align:super;">%</span></p>"""
        labelPercentage.setText(htmlText.replace("{VALUE}", str(sliderValue)))
        self.progressBarValue(sliderValue, progressBarName, color, net_value, net)

    def progressBarValue(self, value, widget, color, net_value, net):

        if net:
            styleSheet = """
                        QFrame{
                            border-radius: 110px;
                            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
                        }
                        """
        else:

            styleSheet = """
            QFrame{
                border-radius: 85px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
            }
            """
        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000

        if net:
            value = net_value
        progress = (100 - value) / 100.0
        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # FIX MAX VALUE
        if value == 100:
            stop_1 = "1.000"
            stop_2 = "1.000"

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2).replace("{COLOR}", color)

        # APPLY STYLESHEET WITH NEW VALUES
        widget.setStyleSheet(newStylesheet)

    def load_settings(self):
        if self.settings.contains("net_speed_unit"):
            self.speed_unit = self.settings.value("net_speed_unit")
            self.ui.comboBox_2.setCurrentText(self.speed_unit)
        if self.settings.contains("cpu_temp_unit"):
            self.temp_unit = self.settings.value("cpu_temp_unit")
            self.ui.comboBox_3.setCurrentText(self.temp_unit)
        if self.settings.contains("net_frequency"):
            self.net_frequency = FREQUENCY_MAPPER.get(int(self.settings.value("net_frequency")), 4)
            self.ui.horizontalSlider.setValue(int(self.settings.value("net_frequency")))
            self.ui.label_15.setText(str(FREQUENCY_MAPPER.get(int(self.settings.value("net_frequency")), "1")) + " Sec")
        if self.settings.contains("cpu_frequency"):
            self.cpu_frequency = FREQUENCY_MAPPER.get(int(self.settings.value("cpu_frequency")), 4)
            self.ui.horizontalSlider_2.setValue(int(self.settings.value("cpu_frequency")))
            self.ui.label_14.setText(str(FREQUENCY_MAPPER.get(int(self.settings.value("cpu_frequency")), "1")) + " Sec")
        if self.settings.contains("ram_frequency"):
            self.ram_frequency = FREQUENCY_MAPPER.get(int(self.settings.value("ram_frequency")), 4)
            self.ui.horizontalSlider_3.setValue(int(self.settings.value("ram_frequency")))
            self.ui.label_16.setText(str(FREQUENCY_MAPPER.get(int(self.settings.value("ram_frequency")), "1")) + " Sec")

    def save_settings(self):
        self.settings.setValue("net_speed_unit", self.ui.comboBox_2.currentText())
        self.settings.setValue("cpu_temp_unit", self.ui.comboBox_3.currentText())
        self.settings.setValue("net_frequency", self.ui.horizontalSlider.value())
        self.settings.setValue("cpu_frequency", self.ui.horizontalSlider_2.value())
        self.settings.setValue("ram_frequency", self.ui.horizontalSlider_3.value())

    def default_frequency(self):
        self.ui.horizontalSlider.setValue(4)
        self.ui.horizontalSlider_2.setValue(4)
        self.ui.horizontalSlider_3.setValue(4)
        self.ui.label_14.setText("1 Sec")
        self.ui.label_15.setText("1 Sec")
        self.ui.label_16.setText("1 Sec")

    def change_net_speed_unit(self):
        self.speed_unit = self.ui.comboBox_2.currentText()
        try:
            self.net_speed_thread.terminate()
            self.start_net_speed_thread()
        except Exception as e:
            print(e)

    def change_temp_unit(self):
        self.temp_unit = self.ui.comboBox_3.currentText()
        try:
            self.cpu_thread.terminate()
            self.start_cpu_thread()
        except Exception as e:
            print(e)

    def change_frequency_net(self):
        self.net_frequency = FREQUENCY_MAPPER.get(self.ui.horizontalSlider.value(), 4)
        self.ui.label_15.setText(str(self.net_frequency) + " Sec")
        try:
            self.net_speed_thread.terminate()
            self.start_net_speed_thread()
        except Exception as e:
            print(e)

    def change_frequency_cpu(self):
        self.cpu_frequency = FREQUENCY_MAPPER.get(self.ui.horizontalSlider_2.value(), 4)
        self.ui.label_14.setText(str(self.cpu_frequency) + " Sec")
        try:
            self.cpu_thread.terminate()
            self.start_cpu_thread()
        except Exception as e:
            print(e)

    def change_frequency_ram(self):
        self.ram_frequency = FREQUENCY_MAPPER.get(self.ui.horizontalSlider_3.value(), 4)
        self.ui.label_16.setText(str(self.ram_frequency) + " Sec")
        try:
            self.ram_thread.terminate()
            self.start_ram_thread()
        except Exception as e:
            print(e)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def load_annimation_data(self):
        self.dummy_data_thread = DummyDataThread()
        self.dummy_data_thread.change_value.connect(self.setProgress_dummy_data)
        self.dummy_data_thread.start()

    def load_cpu_data(self):
        self.ui.label_13.setText(UtilsInfo.get_system_info(self))
        self.start_cpu_thread()

    def load_ram_data(self):
        self.start_ram_thread()

    def load_net_speed_data(self):
        self.start_net_speed_thread()

    def start_cpu_thread(self):
        self.cpu_thread = CpuThread(self.cpu_frequency, self.temp_unit)
        self.cpu_thread.change_value.connect(self.setProgress_cpu)
        self.cpu_thread.start()

    def start_ram_thread(self):
        self.ram_thread = RamThread(self.ram_frequency)
        self.ram_thread.change_value.connect(self.setProgress_ram)
        self.ram_thread.start()

    def start_net_speed_thread(self):
        self.net_speed_thread = NetSpeedThread(self.net_frequency, self.speed_unit)
        self.net_speed_thread.change_value.connect(self.setProgress_net_speed)
        self.net_speed_thread.start()

    def setProgress_cpu(self, value):
        self.setValue(value[0], self.ui.labelPercentageCPU_5, self.ui.circularProgressCPU_5, "rgba(6, 60, 89, 1)")
        html = '<html><head/><body><p><span style=" font-size:9pt; color:#eeeeec;">TEMP: </span><span style=" font-size:9pt; color:#eeeeec;">{VALUE}</span></p></body></html>'
        self.ui.labelCredits_9.setText(html.replace("{VALUE}", str(value[1])))

    def setProgress_ram(self, value):
        self.setValue(value[0], self.ui.labelPercentageRAM_2, self.ui.circularProgressRAM_2, "rgba(6, 60, 89, 1)")
        html = '<html><head/><body><p><span style=" font-size:9pt; color:#eeeeec;">TOTAL: </span><span style=" font-size:9pt; color:#eeeeec;">{VALUE}</span></p></body></html>'
        self.ui.labelCredits_10.setText(html.replace("{VALUE}", value[1]))

    def setProgress_net_speed(self, value):
        graph_value = self.get_graph_value(value)
        show_value = float(value[0][0])
        self.setValue(show_value, self.ui.labelPercentageGPU_3, self.ui.circularProgressGPU_5,
                      "rgba(6, 60, 89, 1)", graph_value, True)
        html = '<html><head/><body><p><span style=" font-size:9pt; color:#eeeeec;">{VALUE}</span></p></body></html>'
        self.ui.labelCredits_5.setText(html.replace("{VALUE}", value[0][1]))

    def get_graph_value(self, value):
        graph_value = 20
        unit = value[0][1]
        value = float(value[0][0])

        if unit in ['Bps', 'Kbps', 'Mbps']:
            value = value / 8

        if unit in ['B/S', 'Bps']:
            if 1 <= value < 1000:
                graph_value = 5 + value / 1000
            else:
                graph_value = 0

        elif unit in ['KB/S', 'Kbps']:
            if value < 10:
                graph_value = 10 + value
            if 10 <= value < 100:
                graph_value = 20 + value / 10
            elif 100 <= value < 1000:
                graph_value = 30 + value / 100

        elif unit in ['MB/S', 'Mbps']:
            if 0 <= value < 6:
                graph_value = 40 + value * 10
            else:
                graph_value = 100

        return int(graph_value)

    def setProgress_dummy_data(self, value):
        value = int(value[0])
        self.setValue(value, self.ui.labelPercentageCPU_5, self.ui.circularProgressCPU_5,
                      "rgba(6, 60, 89, 1)")

        self.setValue(value, self.ui.labelPercentageRAM_2, self.ui.circularProgressRAM_2,
                      "rgba(6, 60, 89, 1)")

        self.setValue(value, self.ui.labelPercentageGPU_3, self.ui.circularProgressGPU_5,
                      "rgba(6, 60, 89, 1)", value, True)

    def credit_button_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def monitor_button_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def setting_button_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def account_button_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    """
        Account functionality :-
    """

    def redirect_to_warlordsoft(self):
        warlord_soft_link = "https://warlordsoftwares.in/warlord_soft/dashboard/"
        webbrowser.open(warlord_soft_link)

    def redirect_to_paypal_donation(self):
        paypal_donation_link = "https://www.paypal.com/paypalme/rishabh3354/5"
        webbrowser.open(paypal_donation_link)

    def redirect_to_rate_snapstore(self):
        QDesktopServices.openUrl(QUrl("snap://htop-pro"))

    def redirect_to_feedback_button(self):
        feedback_link = "https://warlordsoftwares.in/contact_us/"
        webbrowser.open(feedback_link)


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        ## ==> SET INITIAL PROGRESS BAR TO (0) ZERO
        self.progressBarValue(0)

        ## ==> REMOVE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Set background to transparent

        ## ==> APPLY DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.ui.circularBg.setGraphicsEffect(self.shadow)

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(1)

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        ## ==> END ##

    ## DEF TO LOANDING
    ########################################################################
    def progress(self):
        global counter
        global jumper
        value = counter

        # HTML TEXT PERCENTAGE
        htmlText = """<p><span style=" font-size:68pt;">{VALUE}</span><span style=" font-size:58pt; vertical-align:super;">%</span></p>"""

        # REPLACE VALUE
        newHtml = htmlText.replace("{VALUE}", str(jumper))

        if (value > jumper):
            # APPLY NEW PERCENTAGE TEXT
            self.ui.labelPercentage.setText(newHtml)
            jumper += 10

        # SET VALUE TO PROGRESS BAR
        # fix max value error if > than 100
        if value >= 100: value = 1.000
        self.progressBarValue(value)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 0.5

    ## DEF PROGRESS BAR VALUE
    ########################################################################
    def progressBarValue(self, value):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 150px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

        # APPLY STYLESHEET WITH NEW VALUES
        self.ui.circularProgress.setStyleSheet(newStylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    # window = SplashScreen()
    sys.exit(app.exec_())
