# -*- coding: utf-8 -*-
# Author: U.A.V.
# 2020-08
# License : MIT

from modules.vk_module import *
from modules.ip_module import *
from modules.isdn_module import *
from modules.sova_ui import *
from modules.about_ui import *
from modules.share_ui import *
from modules.start_ui import *
from modules.license_ui import *
from modules.rnd_ui import *
from modules.ocid_module import *
from modules.other_module import *
import folium
import datetime
import pandas as pd


from PyQt5.QtGui import QPixmap, QPalette, QColor, QTextCursor
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QStyle, qApp, QApplication, QMenu
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import matplotlib.pyplot as plt
from playsound import playsound
import json
import locale
import os
import re
import requests
import sys
import time
import random as rnd
from collections import Counter
from requests_futures.sessions import FuturesSession


locale.setlocale(locale.LC_ALL, "Russian_Russia.1251")
app_path = str(os.path.dirname(os.path.abspath(sys.argv[0])))

# необходимо записать названия файлов из папки /tokens
token_vk = "token_vk.txt"
token_ip = "token_ip.txt"
token_pstn = "token_pstn.txt"
token_ocd = "token_ocd.txt"
reserve_token_ocd = "token_ocd2.txt"
login_p_vk = "log_pas_vk.txt"
token_mailrep = "token_mailrep.txt"

sites_data_nik = "sites.json"
mcc_base_name = "mcc_codes.json"


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        action_Exit = QtWidgets.QAction(parent)
        action_Exit.setText("Завершить")
        action_Exit.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "control_power_blue.png"))
        action_Exit.triggered.connect(self.exit)
        menu.addAction(action_Exit)
        self.setContextMenu(menu)

    def exit(self):
        QtCore.QCoreApplication.exit()


class ElapsedFuturesSession(FuturesSession):

    def request(self, method, url, *args, **kwargs):
        return super(ElapsedFuturesSession, self).request(method, url, *args, **kwargs)


def get_response(request_future, error_type):
    try:
        rsp = request_future.result()
        if rsp.status_code:
            return rsp, error_type, rsp.elapsed
    except requests.exceptions.HTTPError as errh:
        pass
    except requests.exceptions.ConnectionError as errc:
        pass
    except requests.exceptions.Timeout as errt:
        pass
    except requests.exceptions.RequestException as err:
        pass
    return None, "", -1


class SecondWindow(QtWidgets.QWidget):
    def __init__(self, pix, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.picture = pix
        self.build(self.picture)

    def build(self, pixmap_obj):
        ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_url2.png")
        self.setWindowIcon(ico)
        pixmap = QPixmap(pixmap_obj)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(" ")
        self.label_image = QtWidgets.QLabel(self)
        self.label_image.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        self.mainLayout.addWidget(self.label_image)
        self.setLayout(self.mainLayout)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowCloseButtonHint)
        desktop = QtWidgets.QApplication.desktop()
        self.move(desktop.availableGeometry().center() - self.rect().center())


class RndWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui_rnd = Ui_DialogRando()
        self.ui_rnd.setupUi(self)
        ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico")
        self.setWindowIcon(ico)
        self.ui_rnd.pushButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowCloseButtonHint)
        desktop = QtWidgets.QApplication.desktop()
        self.move(desktop.availableGeometry().center() - self.rect().center())
        self.ui_rnd.pushButton.clicked.connect(self.ReturnFileName)

    def ReturnFileName(self):
        list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'l', 'i', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z',
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        filename = ""
        len_fname = self.ui_rnd.spinBox.value()
        for symbol in range(0, len_fname):
            curr_rand = rnd.randint(0, len(list) - 1)
            filename = filename + list[curr_rand]
        self.ui_rnd.lineEdit.setText(filename)

    def SetMyStyleSheet(self, path=None):
        stream = QtCore.QFile(path)
        stream.open(QtCore.QIODevice.ReadOnly)
        self.setStyleSheet(QtCore.QTextStream(stream).readAll())


class AboutWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui_about = Ui_DialogAbout()
        self.ui_about.setupUi(self)
        self.ui_about.label.setPixmap(QtGui.QPixmap(str(app_path) + "\\sources\\images\\splash_crop.png"))

        try:
            string_to_append = ""
            with open(app_path + "\\sources\\text_data\\about.txt", "r", encoding="utf8") as file:
                string_to_append = file.read()
            self.ui_about.textBrowser.append(string_to_append)

            self.ui_about.textBrowser.moveCursor(QTextCursor.Start)
        except Exception as err:
            print(str(err))

        ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico")
        self.setWindowIcon(ico)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowCloseButtonHint)
        desktop = QtWidgets.QApplication.desktop()
        self.move(desktop.availableGeometry().center() - self.rect().center())

    def SetMyStyleSheet(self, path=None):
        stream = QtCore.QFile(path)
        stream.open(QtCore.QIODevice.ReadOnly)
        self.setStyleSheet(QtCore.QTextStream(stream).readAll())


class ShareWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui_about = Ui_DialogShare()
        self.ui_about.setupUi(self)
        self.ui_about.label.setPixmap(QtGui.QPixmap(str(app_path) + "\\sources\\images\\about.jpg"))
        ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico")
        self.setWindowIcon(ico)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowCloseButtonHint)
        desktop = QtWidgets.QApplication.desktop()
        self.move(desktop.availableGeometry().center() - self.rect().center())

    def SetMyStyleSheet(self, path=None):
        stream = QtCore.QFile(path)
        stream.open(QtCore.QIODevice.ReadOnly)
        self.setStyleSheet(QtCore.QTextStream(stream).readAll())


class StartWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui_start = Ui_DialogStart()
        self.ui_start.setupUi(self)

        try:
            string_to_append = ""
            with open(app_path + "\\sources\\text_data\\tokens_names.txt", "r", encoding="utf8") as file:
                string_to_append = file.read()
            list_strings = string_to_append.split("######")
            self.ui_start.textBrowser.append(list_strings[0])
            self.ui_start.textBrowser.append(
                "<p align=\"center\"> <img src=\"" + app_path + "\\sources\\images\\reg_vk.png\"></p>")
            self.ui_start.textBrowser.append(list_strings[1])
            self.ui_start.textBrowser.append(
                "<p align=\"center\"> <img src=\"" + app_path + "\\sources\\images\\reg_pstn.png\"></p>")
            self.ui_start.textBrowser.append(list_strings[2])
            self.ui_start.textBrowser.append(
                "<p align=\"center\"> <img src=\"" + app_path + "\\sources\\images\\reg_oci.png\"></p>")
            self.ui_start.textBrowser.append(list_strings[3])
            self.ui_start.textBrowser.append(
                "<p align=\"center\"> <img src=\"" + app_path + "\\sources\\images\\reg_ip.png\"></p>")
            self.ui_start.textBrowser.append(list_strings[4])
            self.ui_start.textBrowser.append(
                "<p align=\"center\"> <img src=\"" + app_path + "\\sources\\images\\reg_emailrep.png\"></p>")
            # self.ui_start.textBrowser.append(list_strings[5])
            #
            # self.ui_start.textBrowser.append(list_strings[6])
            self.ui_start.textBrowser.moveCursor(QTextCursor.Start)
        except Exception as err:
            print(str(err))

        ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico")
        self.setWindowIcon(ico)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowCloseButtonHint)
        desktop = QtWidgets.QApplication.desktop()
        self.move(desktop.availableGeometry().center() - self.rect().center())

    def SetMyStyleSheet(self, path=None):
        stream = QtCore.QFile(path)
        stream.open(QtCore.QIODevice.ReadOnly)
        self.setStyleSheet(QtCore.QTextStream(stream).readAll())


class LicenseWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui_lic = Ui_DialogLicense()
        self.ui_lic.setupUi(self)
        try:
            string_to_append = ""
            with open(app_path + "\\sources\\text_data\\copyright.txt", "r", encoding="utf8") as file:
                string_to_append = file.read()
            self.ui_lic.textBrowser.append("<p align=\"center\"><h2>Лицензия OSINT Application \"SOVA\"</h2></p>")
            self.ui_lic.textBrowser.append(
                "<p align=\"center\"> <img src=\"" + app_path + "\\sources\\images\\copy.png\"></p>")
            self.ui_lic.textBrowser.append("Copyright (c) 2020 dev.developych@gmail.com")
            self.ui_lic.textBrowser.append("Все права защищены.")
            self.ui_lic.textBrowser.append(string_to_append)
            self.ui_lic.textBrowser.moveCursor(QTextCursor.Start)
        except Exception as err:
            print(str(err))
        ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico")
        self.setWindowIcon(ico)
        ico_up = QtGui.QIcon(app_path + "\\sources\\images\\ico_collapse.png")
        self.ui_lic.pb_InStart.setIcon(ico_up)
        self.ui_lic.pb_InStart.clicked.connect(self.on_clicked_pb_InStart)
        self.ui_lic.pb_InStart.setCursor(QtCore.Qt.PointingHandCursor)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowCloseButtonHint)
        desktop = QtWidgets.QApplication.desktop()
        self.move(desktop.availableGeometry().center() - self.rect().center())

    def SetMyStyleSheet(self, path=None):
        stream = QtCore.QFile(path)
        stream.open(QtCore.QIODevice.ReadOnly)
        self.setStyleSheet(QtCore.QTextStream(stream).readAll())

    def on_clicked_pb_InStart(self):
        self.ui_lic.textBrowser.moveCursor(QTextCursor.Start)


class MyWin(QtWidgets.QMainWindow):

    sites_data_json_nik = None
    access_token_vk = None
    session_vk = None
    vk_current_result = None
    vk_current_model = None
    vk_searching_name = None
    vk_offset = "0"
    vk_count = "0"
    vk_flag_function = None
    base_mcc = None
    session_insta = None

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        super().__init__(parent)
        self.ShareWin = None
        self.SecondWin = None
        self.AboutWin = None
        self.StartWin = None
        self.LicWin = None
        self.RndWin = None
        self.trayIcon = SystemTrayIcon(QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico"), parent=self)
        self.AboutWin = AboutWindow()
        self.ShareWin = ShareWindow()
        self.StartWin = StartWindow()
        self.LicWin = LicenseWindow()
        self.RndWin = RndWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        VK_GetAppPath(main_path=app_path, path_log_pass=(app_path + "\\tokens\\" + login_p_vk),
                      path_tok=app_path + "\\tokens\\" + token_vk)


        if not os.path.exists(app_path + "\\temp"):
            try:
                os.mkdir(app_path + "\\temp")
            except OSError as err:
                print("Каталог \"temp\" не создан")
                print(err)

        if not os.path.exists(app_path + "\\reports"):
            try:
                os.mkdir(app_path + "\\reports")
            except OSError as err2:
                print("Каталог \"reports\" не создан")
                print(err2)

        if not os.path.exists(app_path + "\\tokens"):
            try:
                os.mkdir(app_path + "\\tokens")
            except OSError as err3:
                print("Каталог \"tokens\" не создан")
                print(err3)


        try:
            self.get_vk_token()
        except:
            self.session_vk = None
            print("Токен ВК не получен")

        try:
            with open(str(app_path) + "\\sources\\text_data\\" + mcc_base_name, "r", encoding="utf8") as file_json:
                self.base_mcc = json.load(file_json)
        except:
            print("База MNC-MCC не загружена")

        try:
            self.get_sites_json()
        except:
            print("База с сайтами не загружена!")

        # заметки для TBrowsers
        self.ui.main_tbShowIMEI.append("<b>Внимание.</b>")
        self.ui.main_tbShowIMEI.append("Введите IMEI (команда *#06#).")
        self.ui.main_tbShowIMEI.append("Примеры: <i>35955601867867, 990002742342332</i>")
        self.ui.main_tbShowWifi.append("<b>Внимание.</b>")
        self.ui.main_tbShowWifi.append("Введите BSSID точки доступа.")
        self.ui.main_tbShowWifi.append("Примеры: <i>00:0C:42:1F:65:E9, A0:F3:C1:3B:6F:90, A0F3C13B6F90, a0f3c13b6f90, A0-F3-C1-3B-6F-90</i>")
        self.ui.main_tbShowEMAIL.append("<b>Внимание.</b>")
        self.ui.main_tbShowEMAIL.append("Введите никнейм пользователя.")
        self.ui.main_tbShowEMAIL.append("Примеры: <i>your_mail@domen.ru</i>")
        self.ui.tbrwsr_ShowBStations.append("<b>Внимание.</b>")
        self.ui.tbrwsr_ShowBStations.append("Результаты можно просмотреть в форме или html-файле (каталог reports). Также можно вывести на карту БС (для этого поставьте галочку)")
        self.ui.tbrwsr_ShowBStations.append("<b>МАКСИМАЛЬНЫЙ РАДИУС = 4</b>")
        self.ui.main_tbShowNikWidth.append("<b>Внимание.</b>")
        self.ui.main_tbShowNikWidth.append("Введите никнейм пользователя.")
        self.ui.main_tbShowNikWidth.append("Примеры: <i>your_nik34534</i>, <i>user12232</i>")
        self.ui.main_tb_ShowUserNameInfo.append("<b>Внимание.</b>")
        self.ui.main_tb_ShowUserNameInfo.append("Введите никнейм пользователя.")
        self.ui.main_tb_ShowUserNameInfo.append("Примеры: <i>your_nik13</i>, <i>username12</i>")
        self.ui.main_tb_ShowUserNameInfo.append("Совет: включите звуковые уведомления и сверните приложение.")
        self.ui.main_tbShowIPInfo.append("<b>Внимание.</b>")
        self.ui.main_tbShowIPInfo.append("Чтобы получить информацию о текущем IP, оставьте поле пустым.")
        self.ui.main_tbShowIPInfo.append("Примеры: <i>8.8.8.8</i>, <i>github.com</i>")
        self.ui.main_tbShowMSISDN.append("<b>Внимание.</b>")
        self.ui.main_tbShowMSISDN.append("Примеры: <i>+79876543210</i>, <i>89123456789,</i>")
        self.ui.main_tbShowMSISDN.append("<i>79876543210</i>, <i>+37423456789</i>")
        self.ui.main_tbShowIMSI.append("<b>Внимание.</b>")
        self.ui.main_tbShowIMSI.append("Введите первые 3-5 цифр IMSI")
        self.ui.main_tbShowIMSI.append("Первые 3 цифры - код страны")
        self.ui.main_tbShowIMSI.append("4,5 цифра - код оператора")
        self.ui.main_tbShowIMSI.append("Примеры: <i>250, 25001, 25099</i>")
        self.ui.vk_textBrowser.append("<b>Внимание.</b>")
        self.ui.vk_textBrowser.append(
            "API vk.com ограничивает количество пользователей, которых можно найти по имени: <b><code>1000</code></b>")
        self.ui.vk_textBrowser.append(
            "В остальном - ограничений нет. В данном модуле использованы возможности REST API")
        self.ui.vk_textBrowser.append(
            "Пример поиска человека по имени: <i>Василий Петров</i>, <i>Петр Иванов</i>")
        self.ui.main_tbShowGeoObjectLatLon.append("<b>Внимание.</b>")
        self.ui.main_tbShowGeoObjectLatLon.append("Введите название объекта.")
        self.ui.main_tbShowGeoObjectLatLon.append("Например: <i>Сочи Театр, Воронеж вокзал</i>")
        self.ui.main_tbShowGeoObjectInfo.append("<b>Внимание.</b>")
        self.ui.main_tbShowGeoObjectInfo.append("Введите широту и долготу объекта или места, появится описание.")
        self.ui.main_tbShowGeoObjectInfo.append("Например: <i>39.0437567,-77.4874416</i>")

        # отключение кнопок:
        self.ui.vk_pbUpTable.setEnabled(False)
        self.ui.vk_pbDownTable.setEnabled(False)
        self.ui.main_progressBarUserName.setValue(0)
        #####################################################################

        ######################################################################

        # соответствие кнопкам:
        # Главная вкладка:
        self.ui.main_pb_ShowIPInfo.clicked.connect(self.on_clicked_main_pbGetIPInfo)
        self.ui.main_pbSearchUser.clicked.connect(self.on_clicked_main_pbGetNicknameInfo)
        self.ui.main_pb_clearISDN.clicked.connect(self.on_clicked_pb_clearSearchISDN)
        self.ui.main_pb_clearIMSI.clicked.connect(self.on_clicked_pb_clearSearchIMSI)
        self.ui.main_pb_ShowISDN.clicked.connect(self.on_clicked_pbShowISDN)
        self.ui.main_pb_ShowIMSI.clicked.connect(self.on_clicked_pbShowIMSI)
        self.ui.main_pb_clearSearchUser.clicked.connect(self.on_clicked_pb_clearSearchUserName)
        self.ui.main_pb_clearSearchIP.clicked.connect(self.on_clicked_pb_clearSearchIP)
        self.ui.main_showBaseSites.clicked.connect(self.on_clicked_showBaseSites)
        self.ui.main_pbChangeStyle.clicked.connect(self.on_clicked_ChangeStyle)
        self.ui.main_pb_ShowGeoLatLon.clicked.connect(self.on_clicked_pb_ShowGeoLatLon)
        self.ui.main_pb_clearGeoObject.clicked.connect(self.on_clicked_pb_clearGeoObject)
        self.ui.main_pb_ShowGeoInfo.clicked.connect(self.on_clicked_pb_ShowGeoInfo)
        self.ui.main_pb_clearGeoInfo.clicked.connect(self.on_clicked_pb_clearGeoInfo)
        self.ui.main_pb_ShowBStations.clicked.connect(self.on_clicked_pb_ShowBStations)
        self.ui.main_pb_clearShowBStations.clicked.connect(self.on_clicked_main_pb_clearShowBStations)
        self.ui.main_pb_ShowNikWidth.clicked.connect(self.on_clicked_main_pb_ShowNikWidth)
        self.ui.main_pb_clearNikWidth.clicked.connect(self.on_clicked_main_pb_clearNikWidth)
        self.ui.main_pb_ShowEMAIL.clicked.connect(self.on_clicked_main_pb_ShowEMAIL)
        self.ui.main_pb_clearEMAIL.clicked.connect(self.on_clicked_main_pb_clearEMAIL)
        self.ui.main_pb_ShowBTSGeo.clicked.connect(self.on_clicked_main_pb_ShowBTSGeo)
        self.ui.main_pb_clearShowBTSGeo.clicked.connect(self.on_clicked_main_pb_clearShowBTSGeo)
        self.ui.main_pb_ShowWifi.clicked.connect(self.on_clicked_main_pb_ShowWifi)
        self.ui.main_pb_clearWifi.clicked.connect(self.on_clicked_main_pb_clearWifi)
        self.ui.main_pb_ShowIMEI.clicked.connect(self.on_clicked_main_pb_ShowIMEI)
        self.ui.main_pb_clearIMEI.clicked.connect(self.on_clicked_main_pb_clearIMEI)
        # VK.COM:
        self.ui.vk_pbSearchByName.clicked.connect(self.on_clicked_vk_pbSearchByName)
        self.ui.vk_pbCheckIsMember.clicked.connect(self.on_clicked_vk_pbCheckIsMember)
        self.ui.vk_pbRunSearchById.clicked.connect(self.on_clicked_vk_pbRunSearchById)
        self.ui.vk_pbRunSearchGroup.clicked.connect(self.on_clicked_vk_pbRunSearchGroup)
        self.ui.vk_pbClearForm.clicked.connect(self.on_clicked_vk_pbClearForm)
        self.ui.vk_pbShowPict.clicked.connect(self.on_clicked_vk_pbShowPict)
        self.ui.vk_pbSaveResult.clicked.connect(self.on_clicked_vk_pbSaveResult)
        self.ui.vk_pbUpTable.clicked.connect(self.on_clicked_vk_pbUpTable)
        self.ui.vk_pbDownTable.clicked.connect(self.on_clicked_vk_pbDownTable)
        self.ui.vk_pbShowDiagrams.clicked.connect(self.on_clicked_vk_pbShowDiagrams)
        self.ui.vk_pbGetID.clicked.connect(self.on_clicked_vk_pbGetID)
        # установка курсоров на кнопки
        # общие кнопки
        self.ui.vk_pbShowPict.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pbChangeStyle.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowIPInfo.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_showBaseSites.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pbSearchUser.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowISDN.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowIMSI.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_checkBox_sound.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearSearchIP.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearIMSI.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearISDN.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearSearchUser.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowGeoLatLon.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearGeoObject.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowGeoInfo.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearGeoInfo.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowBStations.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearShowBStations.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowNikWidth.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearNikWidth.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowEMAIL.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearEMAIL.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowIMEI.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearIMEI.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowWifi.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearWifi.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_ShowBTSGeo.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.main_pb_clearShowBTSGeo.setCursor(QtCore.Qt.PointingHandCursor)
        # self.ui.main_pb_clearShowBStations.setCursor(QtCore.Qt.PointingHandCursor)

        # VK.COM
        self.ui.vk_pbSearchByName.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbCheckIsMember.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbRunSearchById.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbRunSearchGroup.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbClearForm.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbSaveResult.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbUpTable.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbDownTable.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbShowDiagrams.setCursor(QtCore.Qt.PointingHandCursor)
        self.ui.vk_pbGetID.setCursor(QtCore.Qt.PointingHandCursor)

        # загружаем иконки
        ico_get_id = QtGui.QIcon(app_path + "\\sources\\images\\world_key.png")
        ico_url_pic = QtGui.QIcon(app_path + "\\sources\\images\\ico_open_url.png")
        ico_clear = QtGui.QIcon(app_path + "\\sources\\images\\ico_clear.png")
        ico_search = QtGui.QIcon(app_path + "\\sources\\images\\ico_search.png")
        ico_search_id = QtGui.QIcon(app_path + "\\sources\\images\\ico_search_id.png")
        ico_save = QtGui.QIcon(app_path + "\\sources\\images\\ico_properties.png")
        # ico_browser = QtGui.QIcon(app_path + "\\sources\\images\\ico_browser.png")
        ico_up_table = QtGui.QIcon(app_path + "\\sources\\images\\ico_collapse.png")
        ico_down_table = QtGui.QIcon(app_path + "\\sources\\images\\ico_expand.png")
        ico_pie_diagram = QtGui.QIcon(app_path + "\\sources\\images\\ico_pie.png")
        # ico_connections = QtGui.QIcon(app_path + "\\sources\\images\\mind_map.png")
        ico_colour = QtGui.QIcon(app_path + "\\sources\\images\\services.png")
        ico_button_play_green = QtGui.QIcon(app_path + "\\sources\\images\\button_play_green.png")
        ico_button_play_pink = QtGui.QIcon(app_path + "\\sources\\images\\button_play_pink.png")
        ico_button_play_red = QtGui.QIcon(app_path + "\\sources\\images\\button_play_red.png")
        ico_button_play_blue = QtGui.QIcon(app_path + "\\sources\\images\\button_play_blue.png")
        ico_green_open_base = QtGui.QIcon(app_path + "\\sources\\images\\database_start.png")
        ico_sound = QtGui.QIcon(app_path + "\\sources\\images\\ico_sound.png")
        # ico_martian = QtGui.QIcon(app_path + "\\sources\\images\\Bad-Pig.png")
        ico_download = QtGui.QIcon(app_path + "\\sources\\images\\download.png")
        # иконки на ТАБ-виджет

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(app_path + "\\sources\\images\\vk_logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.tabMain.addTab(self.ui.tabVK, icon1, "vk.com")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(app_path + "\\sources\\images\\api_call.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.ui.tabMain.addTab(self.ui.tabCommon, icon, "API + OSINT")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(app_path + "\\sources\\images\\ant.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.tabMain.addTab(self.ui.tabGSM, icon3, "GSM/WIFI")
        # icon5 = QtGui.QIcon()
        # icon5.addPixmap(QtGui.QPixmap(app_path + "\\sources\\images\\twitter_logo.png"), QtGui.QIcon.Normal,
        #                QtGui.QIcon.Off)
        # self.ui.tabMain.addTab(self.ui.tabTwitter, icon5, "")

        # ОБЩИЕ КНОПКИ:
        self.ui.vk_pbShowPict.setIcon(ico_url_pic)
        self.ui.main_pbChangeStyle.setIcon(ico_colour)
        self.ui.main_pbSearchUser.setIcon(ico_button_play_green)
        self.ui.main_pb_ShowISDN.setIcon(ico_button_play_blue)
        self.ui.main_pb_ShowIMSI.setIcon(ico_button_play_blue)
        self.ui.main_pb_ShowIPInfo.setIcon(ico_button_play_pink)
        self.ui.main_pb_clearISDN.setIcon(ico_clear)
        self.ui.main_pb_clearIMSI.setIcon(ico_clear)
        self.ui.main_pb_clearSearchUser.setIcon(ico_clear)
        self.ui.main_pb_clearSearchIP.setIcon(ico_clear)
        self.ui.main_showBaseSites.setIcon(ico_green_open_base)
        self.ui.main_checkBox_sound.setIcon(ico_sound)
        self.ui.main_pb_ShowGeoLatLon.setIcon(ico_button_play_red)
        self.ui.main_pb_clearGeoObject.setIcon(ico_clear)
        self.ui.main_pb_clearGeoInfo.setIcon(ico_clear)
        self.ui.main_pb_ShowGeoInfo.setIcon(ico_button_play_red)
        self.ui.main_pb_ShowBStations.setIcon(ico_button_play_red)
        self.ui.main_pb_clearShowBStations.setIcon(ico_clear)
        self.ui.main_pb_ShowNikWidth.setIcon(ico_button_play_green)
        self.ui.main_pb_ShowEMAIL.setIcon(ico_button_play_green)
        self.ui.main_pb_clearNikWidth.setIcon(ico_clear)
        self.ui.main_pb_clearEMAIL.setIcon(ico_clear)
        self.ui.main_pb_clearWifi.setIcon(ico_clear)
        self.ui.main_pb_clearIMEI.setIcon(ico_clear)
        self.ui.main_pb_ShowIMEI.setIcon(ico_button_play_blue)
        self.ui.main_pb_ShowWifi.setIcon(ico_button_play_blue)
        self.ui.main_pb_ShowBTSGeo.setIcon(ico_button_play_red)
        self.ui.main_pb_clearShowBTSGeo.setIcon(ico_clear)


        # VK.COM
        self.ui.vk_pbClearForm.setIcon(ico_clear)
        self.ui.vk_pbSearchByName.setIcon(ico_search)
        self.ui.vk_pbRunSearchGroup.setIcon(ico_search)
        self.ui.vk_pbRunSearchById.setIcon(ico_search_id)
        self.ui.vk_pbCheckIsMember.setIcon(ico_search_id)
        self.ui.vk_pbSaveResult.setIcon(ico_save)
        self.ui.vk_pbUpTable.setIcon(ico_up_table)
        self.ui.vk_pbDownTable.setIcon(ico_down_table)
        self.ui.vk_pbShowDiagrams.setIcon(ico_pie_diagram)
        self.ui.vk_pbGetID.setIcon(ico_get_id)

        # дополнительно
        self.ui.tabMain.setTabBarAutoHide(True)
        self.ui.tabMain.setMovable(True)

        # меню
        # self.ui.action_startWindow.triggered.connect(self.on_clicked_menu_StartWindow)
        self.ui.action_startWindow.setShortcut(QtGui.QKeySequence("F1"))
        self.ui.action_aboutWindow.setShortcut(QtGui.QKeySequence("F2"))
        self.ui.action_Tray.setShortcut(QtGui.QKeySequence("F3"))
        self.ui.action_startWindow.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "keys.png"))
        self.ui.action_aboutWindow.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "Info.png"))
        self.ui.action_showLicenses.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "Stop.png"))
        self.ui.action_Exit.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "Exit.png"))
        self.ui.action_Tray.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "Fantasy.png"))
        self.ui.action_ErrorsReport.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "share.png"))
        self.ui.action_Randomisator.setIcon(QtGui.QIcon(str(app_path) + "\\sources\\images\\" + "security.png"))

        self.ui.action_aboutWindow.triggered.connect(self.on_clicked_menu_aboutWindow)
        self.ui.action_ErrorsReport.triggered.connect(self.on_clicked_menu_shareWindow)
        self.ui.action_showLicenses.triggered.connect(self.on_clicked_menu_licenseWindow)
        self.ui.action_startWindow.triggered.connect(self.on_clicked_menu_startWindow)
        self.ui.action_Exit.triggered.connect(self.on_clicked_menu_Exit)
        self.ui.action_Tray.triggered.connect(self.on_clicked_menu_Tray)
        self.ui.action_Randomisator.triggered.connect(self.on_clicked_menu_Rnd)

        # self.ui.main_progressBarUserNumber.setEnabled(False)
        # self.ui.main_progressBarUserNumber.setStyleSheet("background: grey; color: white;")
        # self.ui.main_pbSearchNumber.setEnabled(False)
        # self.ui.main_pb_clearSearchUserNumber.setEnabled(False)
        # self.ui.main_editNumber.setEnabled(False)
        # self.ui.main_tb_ShowUserNumber.setEnabled(False)

    def clear_notebook(self):
        self.ui.main_Notebook.clear()

    def on_clicked_menu_Exit(self):
        qApp.quit()

    def on_clicked_menu_Tray(self):
        self.hide()
        self.trayIcon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )
        self.trayIcon.show()
        self.trayIcon.setToolTip('OSINT App')
        self.trayIcon.activated.connect(self.sys_tray_clicking)
        # https://stackoverflow.com/questions/43657890/pyqt5-qsystemtrayicon-activated-signal-not-working
        # https://stackoverflow.com/questions/893984/pyqt-show-menu-in-a-system-tray-application
        # https://www.programcreek.com/python/example/108090/PyQt5.QtWidgets.QSystemTrayIcon
        # https://doc.qt.io/qtforpython/PySide2/QtWidgets/QSystemTrayIcon.html
        # self.hide()
        # self.tray_icon.showMessage("Osint App", "Приложение свернуто в tray...", QSystemTrayIcon.Information, 2000)
        # self.tray_icon.showMessage("Tray Program","Application was minimized to Tray",QSystemTrayIcon.Information,
        #   2000)

    def on_clicked_menu_Rnd(self):
        self.RndWin.show()

    def sys_tray_clicking(self, reason):
        if (reason == self.trayIcon.DoubleClick):
            self.show()
            self.trayIcon.setVisible(False)

    def on_clicked_menu_startWindow(self):
        self.StartWin.show()

    def on_clicked_menu_licenseWindow(self):
        self.LicWin.show()

    def on_clicked_menu_aboutWindow(self):
        self.AboutWin.show()

    def on_clicked_menu_shareWindow(self):
        self.ShareWin.show()

    def load_data(self, sp):
        for i in range(1, 11):  # Имитируем процесс
            time.sleep(0.09)  # Что-то загружаем
            sp.showMessage("Загрузка данных... {0}%".format(i * 10), QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom,
                           QtCore.Qt.black)
            QtWidgets.qApp.processEvents()  # Запускаем оборот цикла

    def closeEvent(self, e):
        result = QtWidgets.QMessageBox.question(self,
                                                "Подтверждение закрытия окна",
                                                "Вы действительно хотите закрыть окно?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            e.accept()
            QtWidgets.QWidget.closeEvent(self, e)
        else:
            e.ignore()

    def on_clicked_pb_clearSearchUserName(self):
        self.ui.main_tb_ShowUserNameInfo.clear()
        self.ui.main_editUserName.clear()
        self.ui.main_progressBarUserName.setValue(0)

    def on_clicked_pb_clearSearchIP(self):
        self.ui.main_tbShowIPInfo.clear()
        self.ui.main_editIP.clear()

    #         VK.COM

    def get_vk_token(self):
        try:
            try:
                self.access_token_vk = open(app_path + "\\tokens\\" + token_vk, "r").read()
            except:
                self.access_token_vk = ReturnToken()
            self.session_vk = API(self.access_token_vk, version="5.103")
        except:
            self.access_token_vk = None

    def on_clicked_vk_pbDownTable(self):
        if self.vk_flag_function:
            if self.vk_flag_function == "users":
                try:
                    self.vk_clear_form()
                    future_vk_offset = int(self.vk_offset) + 400
                    self.vk_offset = str(int(self.vk_offset) + 200)

                    if int(future_vk_offset) <= (int(self.vk_count)):
                        self.ui.vk_pbDownTable.setEnabled(True)
                    else:
                        self.ui.vk_pbDownTable.setEnabled(False)

                    if self.vk_searching_name != "":
                        criteria = "\""
                        criteria += self.vk_searching_name
                        age_list = []
                        if self.ui.vk_CheckAge.isChecked():
                            age_list.append(self.ui.vk_spinAgeFrom.value())
                            age_list.append(self.ui.vk_spinAgeTo.value())
                            criteria += ", возраст: "
                            criteria += str(age_list[0])
                            criteria += "-"
                            criteria += str(age_list[1])
                        else:
                            age_list = None
                        sort_index = self.ui.vk_comboSortRuleUser.currentIndex()
                        sort_r = ""
                        if sort_index == 0:
                            sort_r = "popularity"
                        else:
                            sort_r = "date"
                        online_st = "offline"
                        if self.ui.vk_chooseOnline.isChecked():
                            online_st = "online"
                            criteria += ", online"
                        criteria += "\""
                        result, self.vk_count, self.vk_current_model = VK_Search(self.session_vk,
                                                                                name=self.vk_searching_name,
                                                                                sort_rule=sort_r,
                                                                                online_stat=online_st, age=age_list,
                                                                                offset=str(self.vk_offset))
                        if result == "good":
                            self.ui.vk_pbUpTable.setEnabled(True)
                            self.ui.vk_table.setGeometry(1, 1, 571, 535)
                            self.ui.vk_table.setMinimumHeight(535)
                            self.ui.vk_table.setMaximumHeight(535)
                            self.ui.vk_textBrowser.setGeometry(1, 540, 571, 29)
                            self.ui.vk_textBrowser.setMaximumHeight(29)
                            self.ui.vk_textBrowser.setMinimumHeight(29)
                            if self.vk_offset == "0":
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(self.vk_count) + "</b></p>")
                            else:
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(
                                        self.vk_count) + ", смещение: " + str(self.vk_offset) + "</b></p>")
                            self.ui.vk_table.setModel(self.vk_current_model)
                            self.ui.vk_table.resizeColumnsToContents()
                            self.ui.vk_table.resizeRowsToContents()
                            self.vk_current_result = "<title>Отчет. Поиск пользователей</title>"
                            self.vk_current_result += "<big><b>Источник: vk.com</b></big>"
                            self.vk_current_result += "<br>Поиск пользователей (<i>продолжение выборки</i>)"
                            self.vk_current_result += "<br>Выборка от<big><code> "
                            currDt = datetime.datetime.now()
                            string_time = currDt.strftime('%H:%M:%S %Y.%m.%d')
                            self.vk_current_result += string_time
                            self.vk_current_result += "</code></big><br>Фильтр: <i>"
                            self.vk_current_result += criteria
                            self.vk_current_result += (
                                    "</i><br>Смещение: <i>" + str(self.vk_offset) + "</i>, всего: <i>" + str(
                                self.vk_count) + "</i>")
                            self.vk_current_result += "<br> Заголовок: <i>имя, id, ник, был(а) в сети, пол, д.р., город/страна</i>"
                            self.vk_current_result += "<br>"

                            if future_vk_offset == 1000:
                                self.ui.vk_pbDownTable.setEnabled(False)
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Warning)
                                msg.setText("API vk.com предоставляет 1000 записей. Больше просмотреть нельзя")
                                msg.setWindowTitle("Поиск пользователей")
                                msg.exec_()

                        elif result == "bad":
                            self.handler = None
                            self.session_vk = None
                            self.ui.vk_textBrowser.clear()
                            self.ui.vk_textBrowser.append("Ошибка:")
                            self.ui.vk_textBrowser.append(self.vk_count)
                            model = QStandardItemModel()
                            self.ui.vk_table.setModel(model)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Ошибка")
                            msg.setWindowTitle("Поиск пользователей")
                            msg.exec_()
                        else:
                            self.ui.vk_textBrowser.clear()
                            self.ui.vk_textBrowser.append(
                                "<p></p><p align=\"center\"><h2>Пользователей с таким именем не найдено</p>")
                            model = QStandardItemModel()
                            self.ui.vk_table.setModel(model)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Пользователей с таким именем не найдено")
                            msg.setWindowTitle("Поиск пользователей")
                            msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Введите имя")
                        msg.setWindowTitle("Поиск пользователей")
                        msg.exec_()
                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Внутренняя ошибка")
                    msg.exec_()
            elif self.vk_flag_function == "groups":
                try:
                    self.vk_clear_form()
                    future_vk_offset = int(self.vk_offset) + 400
                    self.vk_offset = str(int(self.vk_offset) + 200)

                    if int(future_vk_offset) <= (int(self.vk_count)):
                        self.ui.vk_pbDownTable.setEnabled(True)
                    else:
                        self.ui.vk_pbDownTable.setEnabled(False)

                    if self.ui.vk_textEditSearchGroup.text() != "":
                        criteria = "\""
                        sort_r = self.ui.vk_cBoxSortRuleGroups.currentIndex()
                        searched_name = self.ui.vk_textEditSearchGroup.text()
                        criteria += searched_name
                        criteria += "\""
                        result, self.vk_count, self.vk_current_model = VK_SearchGroups(self.session_vk,
                                                                                    text=searched_name,
                                                                                    sort_rule=sort_r, count=200,
                                                                                    offset=self.vk_offset)
                        if result == "good":
                            self.ui.vk_pbUpTable.setEnabled(True)
                            self.ui.vk_table.setGeometry(1, 1, 571, 535)
                            self.ui.vk_table.setMinimumHeight(535)
                            self.ui.vk_table.setMaximumHeight(535)
                            self.ui.vk_textBrowser.setGeometry(1, 540, 571, 29)
                            self.ui.vk_textBrowser.setMaximumHeight(29)
                            self.ui.vk_textBrowser.setMinimumHeight(29)
                            if self.vk_offset == "0":
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(self.vk_count) + "</b></p>")
                            else:
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(
                                        self.vk_count) + ", смещение: " + str(
                                        self.vk_offset) + "</b></p>")

                            self.ui.vk_table.setModel(self.vk_current_model)
                            self.ui.vk_table.resizeColumnsToContents()
                            self.ui.vk_table.resizeRowsToContents()
                            self.vk_current_result = "<big><b>Источник: vk.com</b></big>"
                            self.vk_current_result += "<br>Поиск групп(<i>продолжение выборки</i>)"
                            self.vk_current_result += "<br>Выборка от<big><code> "
                            currDt = datetime.datetime.now()
                            string_time = currDt.strftime('%H:%M:%S %Y.%m.%d г.')
                            self.vk_current_result += string_time
                            self.vk_current_result += "</code></big><br>Фильтр: <i>"
                            self.vk_current_result += criteria
                            self.vk_current_result += (
                                    "</i><br>Смещение: <i>" + str(self.vk_offset) + "</i>, всего: <i>" + str(
                                self.vk_count) + "</i>")
                            self.vk_current_result += "</i><br> Заголовок: <i>название, id, открытое, тип, ссылка</i>"
                            self.vk_current_result += "<br>"

                            if future_vk_offset == 1000:
                                self.ui.vk_pbDownTable.setEnabled(False)
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Warning)
                                msg.setText("API vk.com предоставляет 1000 записей. Больше просмотреть нельзя")
                                msg.setWindowTitle("Поиск пользователей")
                                msg.exec_()

                        elif result == "bad":
                            self.handler = None
                            self.session_vk = None
                            self.ui.vk_textBrowser.clear()
                            self.ui.vk_textBrowser.append("Ошибка:")
                            self.ui.vk_textBrowser.append(self.vk_count)
                            model = QStandardItemModel()
                            self.ui.vk_table.setModel(model)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Ошибка")
                            msg.setWindowTitle("Поиск групп")
                            msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Невозможно выполнить запрос.\nПоле ввода пустое")
                        msg.setWindowTitle("Поиск групп")
                        msg.exec_()
                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Внутренняя ошибка")
                    msg.exec_()

    def on_clicked_vk_pbUpTable(self):
        if self.vk_flag_function:
            if self.vk_flag_function == "users":
                try:
                    self.vk_clear_form()
                    self.vk_offset = str(int(self.vk_offset) - 200)
                    self.ui.vk_pbDownTable.setEnabled(True)
                    if int(self.vk_offset) == 0:
                        self.ui.vk_pbUpTable.setEnabled(False)
                    else:
                        self.ui.vk_pbUpTable.setEnabled(True)
                    if self.vk_searching_name != "":
                        criteria = "\""
                        criteria += self.vk_searching_name
                        age_list = []
                        if self.ui.vk_CheckAge.isChecked():
                            age_list.append(self.ui.vk_spinAgeFrom.value())
                            age_list.append(self.ui.vk_spinAgeTo.value())
                            criteria += ", возраст: "
                            criteria += str(age_list[0])
                            criteria += "-"
                            criteria += str(age_list[1])
                        else:
                            age_list = None
                        sort_index = self.ui.vk_comboSortRuleUser.currentIndex()
                        sort_r = ""
                        if sort_index == 0:
                            sort_r = "popularity"
                        else:
                            sort_r = "date"
                        online_st = "offline"
                        if self.ui.vk_chooseOnline.isChecked():
                            online_st = "online"
                            criteria += ", online"
                        criteria += "\""
                        result, self.vk_count, self.vk_current_model = VK_Search(self.session_vk,
                                                                                name=self.vk_searching_name,
                                                                                sort_rule=sort_r,
                                                                                online_stat=online_st,
                                                                                age=age_list,
                                                                                offset=str(self.vk_offset))
                        if result == "good":
                            self.ui.vk_pbDownTable.setEnabled(True)
                            self.ui.vk_table.setGeometry(1, 1, 571, 535)
                            self.ui.vk_table.setMinimumHeight(535)
                            self.ui.vk_table.setMaximumHeight(535)
                            self.ui.vk_textBrowser.setGeometry(1, 540, 571, 29)
                            self.ui.vk_textBrowser.setMaximumHeight(29)
                            self.ui.vk_textBrowser.setMinimumHeight(29)
                            if self.vk_count == "0":
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(self.vk_count) + "</b></p>")
                            else:
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(
                                        self.vk_count) + ", смещение: " + str(
                                        self.vk_offset) + "</b></p>")
                            self.ui.vk_table.setModel(self.vk_current_model)
                            self.ui.vk_table.resizeColumnsToContents()
                            self.ui.vk_table.resizeRowsToContents()
                            self.vk_current_result = "<title>Отчет. Поиск пользователей</title>"
                            self.vk_current_result += "<big><b>Источник: vk.com</b></big>"
                            self.vk_current_result += "<br>Поиск пользователей (<i>продолжение выборки</i>)"
                            self.vk_current_result += "<br>Выборка от<big><code> "
                            currDt = datetime.datetime.now()
                            string_time = currDt.strftime('%H:%M:%S %Y.%m.%d')
                            self.vk_current_result += string_time
                            self.vk_current_result += "</code></big><br>Фильтр: <i>"
                            self.vk_current_result += criteria
                            self.vk_current_result += (
                                    "</i><br>Смещение: <i>" + str(self.vk_offset) + "</i>, всего: <i>" + str(
                                self.vk_count) + "</i>")
                            self.vk_current_result += "<br> Заголовок: <i>имя, id, ник, был(а) в сети, пол, д.р., город/страна</i>"
                            self.vk_current_result += "<br>"
                        elif result == "bad":
                            self.handler = None
                            self.session_vk = None
                            self.ui.vk_textBrowser.clear()
                            self.ui.vk_textBrowser.append("Ошибка:")
                            self.ui.vk_textBrowser.append(self.vk_count)
                            model = QStandardItemModel()
                            self.ui.vk_table.setModel(model)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Ошибка")
                            msg.setWindowTitle("Поиск пользователей")
                            msg.exec_()
                        else:
                            self.ui.vk_textBrowser.clear()
                            self.ui.vk_textBrowser.append(
                                "<p></p><p align=\"center\"><h2>Пользователей с таким именем не найдено</p>")
                            model = QStandardItemModel()
                            self.ui.vk_table.setModel(model)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Пользователей с таким именем не найдено")
                            msg.setWindowTitle("Поиск пользователей")
                            msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Введите имя")
                        msg.setWindowTitle("Поиск пользователей")
                        msg.exec_()
                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Внутренняя ошибка")
                    msg.exec_()
            elif self.vk_flag_function == "groups":
                try:
                    self.vk_clear_form()
                    self.vk_offset = str(int(self.vk_offset) - 200)
                    self.ui.vk_pbDownTable.setEnabled(True)
                    if int(self.vk_offset) == 0:
                        self.ui.vk_pbUpTable.setEnabled(False)
                    else:
                        self.ui.vk_pbUpTable.setEnabled(True)
                    if self.ui.vk_textEditSearchGroup.text() != "":
                        criteria = "\""
                        sort_r = self.ui.vk_cBoxSortRuleGroups.currentIndex()
                        searched_name = self.ui.vk_textEditSearchGroup.text()
                        criteria += searched_name
                        criteria += "\""
                        result, self.vk_count, self.vk_current_model = VK_SearchGroups(self.session_vk,
                                                                                    text=searched_name,
                                                                                    sort_rule=sort_r, count=200,
                                                                                    offset=self.vk_offset)
                        if result == "good":
                            self.ui.vk_pbDownTable.setEnabled(True)
                            self.ui.vk_table.setGeometry(1, 1, 571, 535)
                            self.ui.vk_table.setMinimumHeight(535)
                            self.ui.vk_table.setMaximumHeight(535)
                            self.ui.vk_textBrowser.setGeometry(1, 540, 571, 29)
                            self.ui.vk_textBrowser.setMaximumHeight(29)
                            self.ui.vk_textBrowser.setMinimumHeight(29)
                            if self.vk_offset == "0":
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(self.vk_count) + "</b></p>")
                            else:
                                self.ui.vk_textBrowser.append(
                                    "<p align=\"center\"><b>Всего найдено: " + str(
                                        self.vk_count) + ", смещение: " + str(
                                        self.vk_offset) + "</b></p>")
                            if int(self.vk_count) > 200:
                                self.ui.vk_pbDownTable.setEnabled(True)
                            else:
                                self.ui.vk_pbDownTable.setEnabled(False)
                            self.ui.vk_table.setModel(self.vk_current_model)
                            self.ui.vk_table.resizeColumnsToContents()
                            self.ui.vk_table.resizeRowsToContents()
                            self.vk_current_result = "<big><b>Источник: vk.com</b></big>"
                            self.vk_current_result += "<br>Поиск групп(<i>продолжение выборки</i>)"
                            self.vk_current_result += "<br>Выборка от<big><code> "
                            currDt = datetime.datetime.now()
                            string_time = currDt.strftime('%H:%M:%S %Y.%m.%d г.')
                            self.vk_current_result += string_time
                            self.vk_current_result += "</code></big><br>Фильтр: <i>"
                            self.vk_current_result += criteria
                            self.vk_current_result += (
                                    "</i><br>Смещение: <i>" + str(self.vk_offset) + "</i>, всего: <i>" + str(
                                self.vk_count) + "</i>")
                            self.vk_current_result += "</i><br> Заголовок: <i>название, id, открытое, тип, ссылка</i>"
                            self.vk_current_result += "<br>"
                        elif result == "bad":
                            self.handler = None
                            self.session_vk = None
                            self.ui.vk_textBrowser.clear()
                            self.ui.vk_textBrowser.append("Ошибка:")
                            self.ui.vk_textBrowser.append(self.vk_count)
                            model = QStandardItemModel()
                            self.ui.vk_table.setModel(model)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Ошибка")
                            msg.setWindowTitle("Поиск групп")
                            msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Невозможно выполнить запрос.\nПоле ввода пустое")
                        msg.setWindowTitle("Поиск групп")
                        msg.exec_()
                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Внутренняя ошибка")
                    msg.exec_()

    def on_clicked_vk_pbSearchByName(self):
        self.vk_count = "0"
        self.vk_offset = "0"
        self.vk_flag_function = "users"
        self.vk_clear_form()
        self.vk_searching_name = self.ui.vk_textEditSearchByName.text()
        if self.vk_searching_name != "":
            try:
                criteria = "\""
                criteria += self.vk_searching_name
                age_list = []
                if self.ui.vk_CheckAge.isChecked():
                    age_list.append(self.ui.vk_spinAgeFrom.value())
                    age_list.append(self.ui.vk_spinAgeTo.value())
                    criteria += ", возраст: "
                    criteria += str(age_list[0])
                    criteria += "-"
                    criteria += str(age_list[1])
                else:
                    age_list = None
                sort_index = self.ui.vk_comboSortRuleUser.currentIndex()
                sort_r = ""
                if sort_index == 0:
                    sort_r = "popularity"
                else:
                    sort_r = "date"
                online_st = "offline"
                if self.ui.vk_chooseOnline.isChecked():
                    online_st = "online"
                    criteria += ", online"
                criteria += "\""
                self.vk_clear_form()
                result, self.vk_count, self.vk_current_model = VK_Search(self.session_vk, name=self.vk_searching_name,
                                                                        sort_rule=sort_r, online_stat=online_st,
                                                                        age=age_list, offset=str(self.vk_offset))
                if result == "good":
                    self.ui.vk_table.setGeometry(1, 1, 571, 535)
                    self.ui.vk_table.setMinimumHeight(535)
                    self.ui.vk_table.setMaximumHeight(535)
                    self.ui.vk_textBrowser.setGeometry(1, 540, 571, 29)
                    self.ui.vk_textBrowser.setMaximumHeight(29)
                    self.ui.vk_textBrowser.setMinimumHeight(29)
                    if self.vk_count == "0":
                        self.ui.vk_textBrowser.append(
                            "<p align=\"center\"><b>Пользователей с таким именем не найдено</b></p>")
                    else:
                        self.ui.vk_textBrowser.append(
                            "<p align=\"center\"><b>Всего найдено: " + str(self.vk_count) + "</b></p>")
                    if int(self.vk_count) > 200:
                        self.ui.vk_pbDownTable.setEnabled(True)
                    else:
                        self.ui.vk_pbDownTable.setEnabled(False)

                    self.ui.vk_table.setModel(self.vk_current_model)
                    self.ui.vk_table.resizeColumnsToContents()
                    self.ui.vk_table.resizeRowsToContents()
                    self.vk_current_result = "<title>Отчет. Поиск пользователей</title>"
                    self.vk_current_result += "<big><b>Источник: vk.com</b></big>"
                    self.vk_current_result += "<br>Поиск пользователей"
                    self.vk_current_result += "<br>Выборка от<big><code> "
                    currDt = datetime.datetime.now()
                    string_time = currDt.strftime('%H:%M:%S %Y.%m.%d')
                    self.vk_current_result += string_time
                    self.vk_current_result += "</code></big><br>Фильтр: <i>"
                    self.vk_current_result += criteria
                    self.vk_current_result += ("</i><br>Всего найдено: <i>" + str(self.vk_count) + "</i>")
                    self.vk_current_result += "<br> Заголовок: <i>имя, id, ник, был(а) в сети, пол, д.р., город/страна</i>"
                    self.vk_current_result += "<br>"
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Всего найдено: " + str(self.vk_count))
                    msg.setWindowTitle("Поиск пользователей")
                    msg.exec_()
                elif result == "bad":
                    self.handler = None
                    self.session_vk = None
                    self.ui.vk_textBrowser.clear()
                    self.ui.vk_textBrowser.append("Ошибка:")
                    self.ui.vk_textBrowser.append(self.vk_count)
                    model = QStandardItemModel()
                    self.ui.vk_table.setModel(model)
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Ошибка")
                    msg.setWindowTitle("Поиск пользователей")
                    msg.exec_()
                else:
                    self.ui.vk_textBrowser.clear()
                    self.ui.vk_textBrowser.append(
                        "<p></p><p align=\"center\"><h2>Пользователей с таким именем не найдено</p>")
                    model = QStandardItemModel()
                    self.ui.vk_table.setModel(model)
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Пользователей с таким именем не найдено")
                    msg.setWindowTitle("Поиск пользователей")
                    msg.exec_()
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Внутренняя ошибка")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Введите имя")
            msg.setWindowTitle("Поиск пользователей")
            msg.exec_()

    def on_clicked_vk_pbRunSearchById(self):
        self.vk_current_model = None
        self.vk_current_result = None
        searching_id = self.ui.vk_textEditSearchById.text()
        if searching_id != "":
            try:
                self.vk_clear_form()
                self.ui.vk_textBrowser.setGeometry(1, 1, 571, 540)
                self.ui.vk_textBrowser.setMinimumHeight(540)
                self.ui.vk_textBrowser.setMaximumHeight(540)
                self.ui.vk_table.setGeometry(1, 550, 571, 5)
                self.ui.vk_table.setMaximumHeight(5)
                self.ui.vk_table.setMinimumHeight(5)
                show_fri = self.ui.vk_checkFriends.isChecked()
                show_gr = self.ui.vk_checkGroups.isChecked()
                show_sub = self.ui.vk_checkSubs.isChecked()
                show_fol = self.ui.vk_checkFollowers.isChecked()
                show_wal = self.ui.vk_checkWall.isChecked()
                count_wall_records = 1
                if show_wal == True:
                    count_wall_records = str(self.ui.vk_spinSearchByIdSetRecords.value())
                result, string_result, string_to_report = VK_GetFullInfo(self.session_vk, user_id=searching_id,
                                                                         show_friends=show_fri, show_all_groups=show_gr,
                                                                         show_subs=show_sub, show_followers=show_fol,
                                                                         show_wall=show_wal,
                                                                         wall_records=count_wall_records)
                if result == "good":
                    self.ui.vk_textBrowser.setMinimumHeight(530)
                    self.ui.vk_table.setMaximumHeight(10)
                    self.ui.vk_textBrowser.append(string_result)
                    self.ui.vk_textBrowser.moveCursor(QTextCursor.Start)
                    self.vk_current_result = "<title>Отчет. Выборка</title>"
                    self.vk_current_result += "<big><b>Источник: vk.com</b></big>"
                    self.vk_current_result += string_to_report
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                elif result == "wrong_args":
                    self.handler = None
                    self.session_vk = None
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("ID содержит только цифры")
                    msg.setWindowTitle("Поиск пользователя")
                    msg.exec_()
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Внутренняя ошибка")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Введите ID")
            msg.setWindowTitle("Поиск пользователя")
            msg.exec_()

    def on_clicked_vk_pbCheckIsMember(self):
        if not (
                self.ui.vk_textIsMemberGroupId.text() and self.ui.vk_textIsMemberUserId.text() and self.ui.vk_textIsMemberUserId.text().isdigit()):
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Невозможно выполнить запрос.\nПроверьте поля")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
        else:
            try:
                checking_user_id = self.ui.vk_textIsMemberUserId.text()
                checking_group_id = self.ui.vk_textIsMemberGroupId.text()
                result, result_string = VK_isMemberInGroup(self.session_vk, checking_group_id, checking_user_id)
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                if result == "error":
                    self.handler = None
                    self.session_vk = None
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Невозможно выполнить запрос.\n" + result_string)
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setText(result_string)
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Внутренняя ошибка")
                msg.exec_()

    def on_clicked_vk_pbRunSearchGroup(self):
        self.vk_count = "0"
        self.vk_offset = "0"
        self.vk_flag_function = "groups"
        self.vk_clear_form()
        if self.ui.vk_textEditSearchGroup.text() != "":
            try:
                criteria = "\""
                sort_r = self.ui.vk_cBoxSortRuleGroups.currentIndex()
                searched_name = self.ui.vk_textEditSearchGroup.text()
                criteria += searched_name
                criteria += "\""
                VK_SearchGroups(self.session_vk, text=searched_name, sort_rule=sort_r, count=100)
                result, self.vk_count, self.vk_current_model = VK_SearchGroups(self.session_vk, text=searched_name,
                                                                               sort_rule=sort_r, count=200,
                                                                               offset=self.vk_offset)
                if result == "good":
                    self.ui.vk_table.setGeometry(1, 1, 571, 535)
                    self.ui.vk_table.setMinimumHeight(535)
                    self.ui.vk_table.setMaximumHeight(535)
                    self.ui.vk_textBrowser.setGeometry(1, 540, 571, 29)
                    self.ui.vk_textBrowser.setMaximumHeight(29)
                    self.ui.vk_textBrowser.setMinimumHeight(29)
                    if self.vk_count == "0":
                        self.ui.vk_textBrowser.append(
                            "<p align=\"center\"><b>Сообществ с таким названием не найдено" + "</b></p>")
                    else:
                        self.ui.vk_textBrowser.append(
                            "<p align=\"center\"><b>Всего найдено: " + str(self.vk_count) + "</b></p>")
                    if int(self.vk_count) > 200:
                        self.ui.vk_pbDownTable.setEnabled(True)
                    else:
                        self.ui.vk_pbDownTable.setEnabled(False)
                    self.ui.vk_table.setModel(self.vk_current_model)
                    self.ui.vk_table.resizeColumnsToContents()
                    self.ui.vk_table.resizeRowsToContents()
                    self.vk_current_result = "<title>Отчет. Поиск групп</title>"
                    self.vk_current_result += "<big><b>Источник: vk.com</b></big>"
                    self.vk_current_result += "<br>Поиск групп\n"
                    self.vk_current_result += "<br>Выборка от<big><code> "
                    currDt = datetime.datetime.now()
                    string_time = currDt.strftime('%H:%M:%S %Y.%m.%d г.')
                    self.vk_current_result += string_time
                    self.vk_current_result += "</code></big><br>Фильтр: <i>"
                    self.vk_current_result += criteria
                    self.vk_current_result += ("</i><br>Всего найдено групп: <i>" + str(self.vk_count))
                    self.vk_current_result += "</i><br> Заголовок: <i>название, id, открытое, тип, ссылка</i>"
                    self.vk_current_result += "<br>"
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Найдено " + str(self.vk_count) + " групп")
                    msg.setWindowTitle("Поиск групп")
                    msg.exec_()
                elif result == "bad":
                    self.handler = None
                    self.session_vk = None
                    self.ui.vk_textBrowser.clear()
                    self.ui.vk_textBrowser.append("Ошибка:")
                    self.ui.vk_textBrowser.append(self.vk_count)
                    model = QStandardItemModel()
                    self.ui.vk_table.setModel(model)
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Ошибка")
                    msg.setWindowTitle("Поиск групп")
                    msg.exec_()
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Внутренняя ошибка")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Невозможно выполнить запрос.\nПоле ввода пустое")
            msg.setWindowTitle("Поиск групп")
            msg.exec_()

    def on_clicked_vk_pbShowPict(self):
        photo_url = self.ui.vk_editShowPict.text()
        if photo_url != "":
            try:
                f_path = app_path + "\\temp\\temp.jpg"
                if os.path.exists(f_path):
                    os.remove(f_path)
                urllib.request.urlretrieve(photo_url, f_path)
                self.SecondWin = SecondWindow(f_path)
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                self.SecondWin.show()
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Внутренняя ошибка")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Пустое поле ввода")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def on_clicked_vk_pbSaveResult(self):
        if self.vk_current_result != None:
            FileName = app_path + "\\reports\\VK_report_"
            currDt = datetime.datetime.now()
            string_time = currDt.strftime('%Y.%m.%d_%H.%M.%S')
            FileName += string_time
            string_to_message = "Файл сохранен. Имя:\n"
            string_to_message += FileName
            FileName += ".html"
            with open(FileName, "w", encoding='utf-8') as file:
                file.write(self.vk_current_result)
            if self.vk_current_model != None:
                self.vk_save_to_file_from_model(model=self.vk_current_model, filename=FileName)
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\end.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setText(string_to_message)
            msg.setWindowTitle("Сохранение результата")
            msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Невозможно сохранить. Нет данных")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def vk_save_to_file_from_model(self, model, filename):
        column_count = model.columnCount()
        row_count = model.rowCount()
        for i in range(0, row_count):
            curr_string = "<br>"
            curr_string += str(i + 1)
            for j in range(0, column_count):
                item_text = model.item(i, j).text()
                if j == 0:
                    curr_string += ". "
                    curr_string += item_text
                else:
                    curr_string += ", "
                    curr_string += item_text
            with open(filename, "a", encoding='utf-8') as file:
                file.write(curr_string)

    def on_clicked_vk_pbClearForm(self):
        self.vk_clear_form()
        self.ui.vk_pbDownTable.setEnabled(False)
        self.ui.vk_pbUpTable.setEnabled(False)
        self.vk_flag_function = None
        self.ui.vk_textEditSearchGroup.clear()
        self.ui.vk_textEditSearchByName.clear()
        self.ui.vk_textEditSearchById.clear()
        self.ui.vk_textIsMemberGroupId.clear()
        self.ui.vk_textIsMemberUserId.clear()
        self.ui.vk_CheckAge.setChecked(False)
        self.ui.vk_chooseOnline.setChecked(False)
        self.ui.vk_checkFollowers.setChecked(False)
        self.ui.vk_checkFriends.setChecked(False)
        self.ui.vk_checkGroups.setChecked(False)
        self.ui.vk_checkSubs.setChecked(False)
        self.ui.vk_checkWall.setChecked(False)
        self.ui.vk_spinSearchByIdSetRecords.setValue(1)
        self.ui.vk_spinAgeTo.setValue(60)
        self.ui.vk_spinAgeFrom.setValue(15)
        self.ui.vk_comboSortRuleUser.setCurrentIndex(0)
        self.ui.vk_cBoxSortRuleGroups.setCurrentIndex(0)
        self.ui.vk_editShowPict.clear()

    def vk_clear_form(self):
        self.ui.vk_textBrowser.clear()
        model = QStandardItemModel()
        self.vk_current_result = None
        self.vk_current_model = None
        self.ui.vk_table.setModel(model)
        self.ui.vk_table.setGeometry(1, 1, 571, 281)
        self.ui.vk_table.setMinimumHeight(280)
        self.ui.vk_table.setMaximumHeight(280)
        self.ui.vk_textBrowser.setGeometry(1, 288, 571, 280)
        self.ui.vk_textBrowser.setMaximumHeight(275)
        self.ui.vk_textBrowser.setMinimumHeight(275)

    def ReturnNiceStringFromDict(self, dict_=None, title_df=None):
        string_to_return = "<p><br><b>" + title_df + "</b><br>"
        if title_df == "Выборка по возрасту:":
            string_to_return += "<br>[возраст]: [частота]</br>"
        elif title_df == "Выборка по полу:":
            string_to_return += "<br>[пол]: [частота]</br>"
        elif title_df == "Выборка по городам:":
            string_to_return += "<br>[город]: [частота]</br>"
        elif title_df == "Выборка по странам:":
            string_to_return += "<br>[страна]: [частота]</br>"
        list_d = list(dict_.items())
        list_d.sort(key=lambda i: i[1], reverse=True)
        for key, value in list_d:
            string_to_return += ("<br>" + str(key) + ": " + str(value))
        string_to_return += "</p>"
        return string_to_return

    def ReturnNormDict(self, dict_=None, min=None):
        new_dict = {}
        for key, value in dict_.items():
            if value > min:
                new_dict[key] = value
            else:
                temp_value = new_dict.get("менее 1%")
                if temp_value != None:
                    temp_value += value
                    new_dict["менее 1%"] = temp_value
                else:
                    new_dict["менее 1%"] = value
        return new_dict

    def on_clicked_vk_pbShowDiagrams(self):
        user_id = self.ui.vk_textUserIDForGraphics.text()
        if user_id != "":
            try:
                result1, result2, report3 = VK_GetUsrInfo(self.session_vk, user=user_id)
                if result1 == "good":
                    self.vk_clear_form()
                    self.vk_current_result = "<title>Отчет. Выборка</title>"
                    self.vk_current_result += report3
                string_result, data = VK_MakeDataForDiagrams(self.session_vk, user=user_id)
                if string_result != "<p align=\"center\"><b>Выборка сделана, количество друзей: 0</b></p>" and string_result != "<p align=\"center\"><h2>Повторите запрос, нужно обновить токен</h2></p>" and string_result != "<p align=\"center\"><h2>Невозможно отобразить друзей пользователя</h2></p>":
                    self.ui.vk_textBrowser.setGeometry(1, 1, 571, 540)
                    self.ui.vk_textBrowser.setMinimumHeight(540)
                    self.ui.vk_textBrowser.setMaximumHeight(540)
                    self.ui.vk_table.setGeometry(1, 550, 571, 5)
                    self.ui.vk_table.setMaximumHeight(5)
                    self.ui.vk_table.setMinimumHeight(5)
                    self.vk_current_result += string_result
                    count_items = len(data['sex'])
                    min_part_ = int(int(count_items) * 0.01)
                    data_sex = Counter(data['sex'])
                    data_age = Counter(data['age'])
                    data_city = Counter(data['city'])
                    data_country = Counter(data['country'])
                    data_city_norm = self.ReturnNormDict(dict_=dict(data_city), min=min_part_)
                    data_age_norm = self.ReturnNormDict(dict_=dict(data_age), min=min_part_)
                    data_sex_norm = self.ReturnNormDict(dict_=dict(data_sex), min=min_part_)
                    data_country_norm = self.ReturnNormDict(dict_=dict(data_country), min=min_part_)
                    self.vk_current_result += "<br>В случае, если по какому-то показателю его значение не превышает 1% от общих частот, данное значение будет отнесено к \"менее 1%\"</br>"
                    self.vk_current_result += "<br>Например, при количестве друзей 700, какой-либо из показателей, меньший 7 будет отнесен к общей категории \"менее 1%\".</br>"
                    string_sex = self.ReturnNiceStringFromDict(dict_=data_sex_norm, title_df="Выборка по полу:")
                    self.vk_current_result += string_sex
                    string_age = self.ReturnNiceStringFromDict(dict_=data_age_norm, title_df="Выборка по возрасту:")
                    self.vk_current_result += string_age
                    string_cty = self.ReturnNiceStringFromDict(dict_=data_city_norm, title_df="Выборка по городам:")
                    self.vk_current_result += string_cty
                    string_cntry = self.ReturnNiceStringFromDict(dict_=data_country_norm,
                                                                 title_df="Выборка по странам:")
                    self.vk_current_result += string_cntry

                    df = pd.DataFrame.from_dict({
                        'Пол': data_sex_norm,
                        'Возраст': data_age_norm,
                        'Город': data_city_norm,
                        'Страна': data_country_norm
                    })
                    try:
                        string_title = "Друзья пользователя id" + user_id
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                        df.plot.pie(title=string_title, subplots=True, legend=True, layout=(2, 2), figsize=(8, 8))
                    except Exception as e:
                        print(e)
                    plt.tight_layout()
                    self.ui.vk_textBrowser.append(self.vk_current_result)
                    self.ui.vk_textBrowser.moveCursor(QTextCursor.Start)
                    plt.show()
                else:
                    self.vk_clear_form()
                    self.ui.vk_textBrowser.append("<br></br><br></br>" + string_result)
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Внутренняя ошибка")
                msg.exec_()

    def make_adjacency(self, user_id):
        '''Создать таблицу инцидентности
        в виде словаря в формате (узел, список узлов)
        user_id: id пользователя, для которого требуется
                 построить граф друзей
        Возвращает: словарь и список идентификаторов друзей
        '''
        dic = {}
        ids = None
        count = None
        try:
            count, ids = VK_GetFriendsId(self.session_vk, user=user_id)
        except Exception as e:
            print("проблема make_adjacency_1: ", e, datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds'))
        print("DEBUG: make_adjacency, всего друзей: " + str(count) + ", ",
              datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds'))
        count_friends = 0
        for friend in ids:
            count_friends += 1
            print("DEBUG: make_adjacency, Друг №" + str(count_friends) + ", ",
                  datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds'))
            cnt, friend_friends_list = VK_GetFriendsId(self.session_vk, user=user_id)
            dic[friend] = {i for i in friend_friends_list if i in ids}
        return dic, ids

    def on_clicked_vk_pbGetID(self):
        searching_url = self.ui.vk_textEdiGetID.text()
        try:
            if searching_url != "":
                list_split = searching_url.split("/")
                nickname = list_split[-1]
                type, id = VK_GetTypeID(self.session_vk, text_str=nickname)
                if type == "user" or type == "group" or type == "application":
                    string_to_msgBox = ("Запрос выполнен!\nТип: " + type)
                    self.ui.vk_textEdiGetID.setText(str(id))
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(string_to_msgBox)
                    msg.setWindowTitle("Успех")
                    msg.exec_()
                elif type == "no users":
                    self.ui.vk_textEdiGetID.setText(str(id))
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Запрос выполнен!\nВК не знает таких")
                    msg.setWindowTitle("Успех")
                    msg.exec_()
                else:
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(type)
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
        except Exception as e:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(str(e))
            msg.setWindowTitle("Внутренняя ошибка")
            msg.exec_()


    #      SNOOP Project + NICKNAMES_WIDTH

    def get_sites_json(self):
        try:
            with open(str(app_path) + "\\sources\\text_data\\" + sites_data_nik, "r", encoding="utf8") as file_json:
                self.sites_data_json_nik = json.load(file_json)
                count_sites = len(self.sites_data_json_nik)
                self.ui.main_progressBarUserName.setMaximum(count_sites)
        except:
            self.ui.main_showBaseSites.setEnabled(False)

    def snoop_engine(self, username=None, site_data=None):
        # Создать сеанс на основе методологии запроса.
        counter_sites = 0
        counter_sites_ok = 0
        try:
            underlying_session = requests.session()
            underlying_request = requests.Request()
        except:
            print("underlying_session...")
        # Рабочий лимит 20+
        try:
            if len(site_data) >= 20:
                max_workers = 20
            else:
                max_workers = len(site_data)
        except:
            print("max_workers")
        # Создать многопоточный сеанс для всех запросов.
        try:
            session = ElapsedFuturesSession(max_workers=max_workers, session=underlying_session)
        except Exception as e:
            print("session = ElapsedFuturesSession...", e)
        # Результаты анализа всех сайтов.
        results_total = {}
        # Создание futures на все запросы. Это позволит распараллетить запросы.
        for social_network, net_info in site_data.items():
            #        print([iz for iz in site_data]) #Тест вывода ключей (названия сайтов)
            #        print(social_network) #(названия сайтов, строки)
            # Результаты анализа конкретного сайта.
            results_site = {}
            # Запись URL основного сайта и флага страные (сопоставление с data.json).
            results_site['flagcountry'] = net_info.get("country")
            results_site['flagcountryklas'] = net_info.get("country_klas")
            results_site['url_main'] = net_info.get("urlMain")
            # Пользовательский user-agent браузера, некоторые сайты от этого зависят напрямую.
            # Временно поставил самый популярный, чтобы не думали, что запросы идут от ботов.
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            }

            if "headers" in net_info:
                # Переопределить / добавить любые дополнительные заголовки, необходимые для данного сайта.
                headers.update(net_info["headers"])

            # Не делать запрос, если имя пользователя не подходит для сайта.
            exclusionYES = net_info.get("exclusion")
            if exclusionYES and re.search(exclusionYES, username):
                # Не нужно делать проверку на сайте: если это имя пользователя не допускается.

                results_site["exists"] = "прочерк"
                results_site["url_user"] = ""
                results_site['countryCSV'] = ""
                results_site['http_status'] = ""
                results_site['response_text'] = ""
                results_site['check_time_ms'] = ""
                results_site['response_time_ms'] = ""
                results_site['response_time_site_ms'] = ""
            else:
                # URL пользователя на сайте (если он существует).
                url = net_info["url"].format(username)
                results_site["url_user"] = url
                url_probe = net_info.get("urlProbe")
                if url_probe is None:
                    # URL-адрес — является обычным, который видят люди в Интернете.
                    url_probe = url
                else:
                    # Существует специальный URL (обычно о нем мы не догадываемся/api) для проверки существования отдельно юзера.
                    url_probe = url_probe.format(username)

                # Если нужен только статус кода, не загружать код страницы.
                if net_info["errоrTypе"] == 'status_code':
                    request_method = session.head
                else:
                    request_method = session.get

                if net_info["errоrTypе"] == "response_url":
                    # Сайт перенаправляет запрос на другой URL, если имя пользователя не существует.
                    # Имя найдено. Запретить перенаправление чтобы захватить статус кода из первоначального url.
                    allow_redirects = False
                else:
                    # Разрешить любой редирект, который хочет сделать сайт.
                    # Окончательным результатом запроса будет то, что доступно.
                    allow_redirects = True

                future = request_method(url=url_probe, headers=headers, allow_redirects=allow_redirects)

                # Сохранить future in data для последующего доступа.
                net_info["request_future"] = future
            # Добавлять результаты этого сайта в окончательный словарь со всеми другими результатами.
            results_total[social_network] = results_site

        # print(results_site) # Проверка записи на успех.
        for social_network, net_info in site_data.items():
            counter_sites = counter_sites + 1
            results_site = results_total.get(social_network)
            # Получить другую информацию сайта снова.
            url = results_site.get("url_user")
            countryA = results_site.get("flagcountry")
            countryB = results_site.get("flagcountryklas")
            exists = results_site.get("exists")
            if exists is not None:
                continue
            # Получить ожидаемый тип данных 4 методов.
            error_type = net_info["errоrTypе"]
            # Данные по умолчанию в случае каких-либо сбоев в выполнении запроса.
            http_status = "*???"
            response_text = ""
            # Получить future и убедиться, что оно закончено.
            future = net_info["request_future"]
            r, error_type, response_time = get_response(request_future=future,
                                                        error_type=error_type)
            # Попытка получить информацию запроса.
            try:
                http_status = r.status_code
            except:
                pass
            try:
                response_text = r.text.encode(r.encoding)
            except:
                pass
            # Проверка, 4 метода; #1.
            # Ответы message (разные локации).
            if error_type == "message":
                error = net_info.get("errorMsg")
                error2 = net_info.get("errorMsg2")
                if error2 in r.text:
                    exists = "увы"
                elif error in r.text:
                    exists = "увы"
                else:
                    exists = "найден!"
            # Проверка, 4 метода; #2.
            # Проверка username при статусе 301 и 303 (перенаправление и соль).
            elif error_type == "redirection":
                rr = requests.get(url, allow_redirects=False)
                if rr.status_code == 301 or rr.status_code == 303:
                    exists = "найден!"
                else:
                    exists = "увы"
            # Проверка, 4 метода; #3.
            # Проверяет, является ли код состояния ответа 2..
            elif error_type == "status_code":
                if not r.status_code >= 300 or r.status_code < 200:
                    exists = "найден!"
                else:
                    exists = "увы"
            # Проверка, 4 метода; #4
            # Перенаправление.
            elif error_type == "response_url":
                if 200 <= r.status_code < 300:
                    exists = "найден!"
                else:
                    exists = "увы"

            # Если все 4 метода не сработали, например, из-за ошибки доступа.
            else:
                exists = "блок"

            if exists == "найден!":
                network_string = "<br><b>" + str(social_network) + ":</b></br>"
                self.ui.main_tb_ShowUserNameInfo.append(network_string)
                url_string = "<i>" + str(url) + "</i>"
                self.ui.main_tb_ShowUserNameInfo.append(url_string)
                self.ui.main_progressBarUserName.setValue(counter_sites)
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\ok.wav")
                counter_sites_ok = counter_sites_ok + 1
            else:
                self.ui.main_progressBarUserName.setValue(counter_sites)
        max_count = self.ui.main_progressBarUserName.maximum()
        self.ui.main_progressBarUserName.setValue(max_count)
        if self.ui.main_checkBox_sound.isChecked():
            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
        self.ui.main_editUserName.setText((username + ": " + str(counter_sites_ok)))
        msg = QMessageBox()
        string_to_msg = "Поиск завершен! Всего: " + str(counter_sites_ok) + " совпадений(я,е)"
        msg.setIcon(QMessageBox.Information)
        msg.setText(string_to_msg)
        msg.setWindowTitle("Уведомление")
        msg.exec_()

    def on_clicked_main_pbGetNicknameInfo(self):
        username_from_form = self.ui.main_editUserName.text()
        if username_from_form != "":
            self.ui.main_tb_ShowUserNameInfo.clear()
            self.ui.main_progressBarUserName.setValue(0)
            self.snoop_engine(username=username_from_form, site_data=self.sites_data_json_nik)
            self.ui.main_tb_ShowUserNameInfo.moveCursor(QTextCursor.Start)
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Введите никнейм")
            msg.setWindowTitle("Нет данных")
            msg.exec_()

    def on_clicked_showBaseSites(self):
        self.ui.main_progressBarUserName.setValue(0)
        self.ui.main_tb_ShowUserNameInfo.clear()
        with open(str(app_path) + "\\sources\\text_data\\" + sites_data_nik, "r", encoding="utf8") as file:
            sites_data_json_nik = json.load(file)
            for idx, site in enumerate(sites_data_json_nik):
                self.ui.main_tb_ShowUserNameInfo.append(str(idx+1) + ". " + str(site))
        self.ui.main_tb_ShowUserNameInfo.moveCursor(QTextCursor.Start)

    def on_clicked_main_pb_ShowNikWidth(self):
        username_from_form = self.ui.main_editNikWidth.text()
        if username_from_form != "":
            try:
                self.ui.main_tbShowNikWidth.clear()
                try:
                    self.get_vk_token()
                except:
                    pass
                str_to_ret = Search_NickName(username_from_form, self.session_vk)
                self.ui.main_tbShowNikWidth.moveCursor(QTextCursor.Start)
                if str_to_ret != "NULL":
                    self.ui.main_tbShowNikWidth.append(str_to_ret)
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Ничего не найдено!")
                    msg.setWindowTitle("Уведомление")
                    msg.exec_()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Ошибка: " + str(e))
                msg.setWindowTitle("Уведомление")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Введите никнейм")
            msg.setWindowTitle("Нет данных")
            msg.exec_()
    
    def on_clicked_main_pb_clearNikWidth(self):
        self.ui.main_editNikWidth.clear()
        self.ui.main_tbShowNikWidth.clear()

    #    REST API   // ГЛАВНОЕ ОКНО

    def on_clicked_main_pbGetIPInfo(self):
        try:
            self.ui.main_tbShowIPInfo.clear()
            curr_token_ip = None
            searching_ip = self.ui.main_editIP.text()
            with open((app_path + "\\tokens\\" + token_ip), "r") as f:
                curr_token_ip = f.read()
            curr_string = IpInfo_Io(TOKEN=curr_token_ip, ip=searching_ip)
            if curr_string != "Empty":
                self.ui.main_tbShowIPInfo.append(curr_string)
            curr_string = IP_API_com(ip=searching_ip)
            if curr_string != "Empty":
                self.ui.main_tbShowIPInfo.append(curr_string)
            curr_string = Free_Ipwhois_Io(ip=searching_ip)
            if curr_string != "Empty":
                self.ui.main_tbShowIPInfo.append(curr_string)
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\end.wav")
        except:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Ошибка")
            msg.setWindowTitle("Уведомление")
            msg.exec_()

    def on_clicked_ChangeStyle(self):
        """
        import PyQt5.QtWidgets
        print(PyQt5.QtWidgets.QStyleFactory.keys()) # посмотреть все стили
        """
        NewStyle = None
        Path_to_qss = None
        NewStyle_index = self.ui.main_comboBox_style.currentIndex()
        if NewStyle_index == 0:
            NewStyle = "Fusion"
            Path_to_qss = str(app_path) + "\\sources\\qss\\default.qss"
            # self.ui.main_Notebook.setStyleSheet("background-color: rgb(223,224,230)")
        elif NewStyle_index == 1:
            NewStyle = "Fusion"
            Path_to_qss = str(app_path) + "\\sources\\qss\\dark_orange.qss"
        elif NewStyle_index == 2:
            NewStyle = "Fusion"
            Path_to_qss = str(app_path) + "\\sources\\qss\\silver.qss"
        try:
            app.setStyle(NewStyle)
            self.SetMyStyleSheet(Path_to_qss)
            self.AboutWin.SetMyStyleSheet(Path_to_qss)
            self.ShareWin.SetMyStyleSheet(Path_to_qss)
            self.StartWin.SetMyStyleSheet(Path_to_qss)
            self.LicWin.SetMyStyleSheet(Path_to_qss)
            self.RndWin.SetMyStyleSheet(Path_to_qss)
            app.setStyle(NewStyle)
            self.SetMyStyleSheet(Path_to_qss)
            self.AboutWin.SetMyStyleSheet(Path_to_qss)
            self.ShareWin.SetMyStyleSheet(Path_to_qss)
            self.StartWin.SetMyStyleSheet(Path_to_qss)
            self.LicWin.SetMyStyleSheet(Path_to_qss)
            self.RndWin.SetMyStyleSheet(Path_to_qss)
        except Exception as E:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(str(E))
            msg.setWindowTitle("Внутренняя ошибка")
            msg.exec_()

    def SetMyStyleSheet(self, path=None):
        stream = QtCore.QFile(path)
        stream.open(QtCore.QIODevice.ReadOnly)
        self.setStyleSheet(QtCore.QTextStream(stream).readAll())
        self.ui.tabMain.setStyleSheet(QtCore.QTextStream(stream).readAll())
        self.ui.groupBox_3.setStyleSheet(QtCore.QTextStream(stream).readAll())
        self.ui.main_Notebook.setStyleSheet(QtCore.QTextStream(stream).readAll())

    def on_clicked_pbShowISDN(self):
        isdn_from_form = self.ui.main_editISDN.text()
        fst_good = False
        snd_good = False
        
        if isdn_from_form != "":
            self.ui.main_tbShowMSISDN.clear()
            try:
                curr_str = ApiSubnets(num=isdn_from_form)
                if curr_str != "empty" and curr_str != None:
                    self.ui.main_tbShowMSISDN.append("<b>rosreestr.subnets.ru</b>:")
                    self.ui.main_tbShowMSISDN.append(curr_str)
                    fst_good = True
            except:
                pass
            try:
                curr_str = ApiRegiusName(num=isdn_from_form)
                if curr_str != "empty":
                    if fst_good == True:
                        # self.ui.main_tbShowMSISDN.append("<br></br>")
                        self.ui.main_tbShowMSISDN.append("<b>api.regius.name</b>:")
                        self.ui.main_tbShowMSISDN.append(curr_str)
                        snd_good = True
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    else:
                        self.ui.main_tbShowMSISDN.append("<b>api.regius.name</b>:")
                        self.ui.main_tbShowMSISDN.append(curr_str)
                        snd_good = True
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
            except:
                pass
            if fst_good == False and snd_good == False:
                try:
                    curr_token_pstn = None
                    try:
                        with open((str(app_path) + "\\tokens\\" + token_pstn), "r") as f:
                            curr_token_pstn = f.read()
                    except:
                        pass
                    curr_str = ApiHtmlWeb(num=isdn_from_form, TOKEN=curr_token_pstn)
                    if curr_str != "empty":
                        self.ui.main_tbShowMSISDN.append("<b>htmlweb.ru</b>:")
                        self.ui.main_tbShowMSISDN.append(curr_str)
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    else:
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.NoIcon)
                        msg.setText("Ничего не найдено")
                        msg.setWindowTitle("Уведомление")
                        msg.exec_()
                except Exception as e:
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Внутренняя ошибка")
                    msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Поле ввода пусто")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def on_clicked_pb_clearSearchISDN(self):
        self.ui.main_editISDN.clear()
        self.ui.main_tbShowMSISDN.clear()

    def on_clicked_pb_clearSearchIMSI(self):
        self.ui.main_editIMSI.clear()
        self.ui.main_tbShowIMSI.clear()

    def on_clicked_pbShowIMSI(self):
        imsi_from_form = self.ui.main_editIMSI.text()
        if imsi_from_form != "":
            self.ui.main_tbShowIMSI.clear()
            try:
                info = get_imsi_info_new_func(app_path, imsi_from_form)
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                self.ui.main_tbShowIMSI.append(info)
            except:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                self.ui.textBrowser_BTSGeo.append("<p align=\"center\"><h4>Ничего не найдено!</h4></p>")
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Поле ввода пусто")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def on_clicked_main_pb_ShowEMAIL(self):
        mail_from_form = self.ui.main_editEMAIL.text()
        if mail_from_form != "":
            curr_token_mail = None
            self.ui.main_tbShowEMAIL.clear()
            try:
                with open((str(app_path) + "\\tokens\\" + token_mailrep), "r") as f:
                    curr_token_mail = f.read()
                if curr_token_mail != "":
                    str_to_ret = MailReputation(curr_token_mail, mail_from_form)
                    if str_to_ret:
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                        self.ui.main_tbShowEMAIL.append(str_to_ret)
                    else:
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Ошибка")
                        msg.setWindowTitle("Уведомление")
                        msg.exec_()    
                else:
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Токен не записан в текстовый файл")
                    msg.setWindowTitle("Уведомление")
                    msg.exec_() 
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Ошибка: " + str(e))
                msg.setWindowTitle("Уведомление")
                msg.exec_()    
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Поле ввода пустое")
            msg.setWindowTitle("Уведомление")
            msg.exec_()

    def on_clicked_main_pb_clearEMAIL(self):
        self.ui.main_editEMAIL.clear()
        self.ui.main_tbShowEMAIL.clear()

    def on_clicked_main_pb_ShowWifi(self):
        bssid = self.ui.main_edit_Wifi.text()
        if bssid != "":
            self.ui.main_tbShowWifi.clear()
            try:
                info = get_coord_wifi_inikov(bssid)
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                if info[0]:
                    self.ui.main_tbShowWifi.append("<p align=\"center\"><h3>mylnikov.org</h3></p>")
                    self.ui.main_tbShowWifi.append(str(info[0]) + "," + str(info[1]) + "; точность: " + str(info[2]) + " м")
                else:
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                    self.ui.main_tbShowWifi.append("<p align=\"center\"><h4>Ничего не найдено!</h4></p>")
            except:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                self.ui.main_tbShowWifi.append("<p align=\"center\"><h4>Ничего не найдено!</h4></p>")
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Поле ввода пусто")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def on_clicked_main_pb_clearWifi(self):
        self.ui.main_edit_Wifi.clear()
        self.ui.main_tbShowWifi.clear()

    def on_clicked_main_pb_clearIMEI(self):
        self.ui.main_editIMEI.clear()
        self.ui.main_tbShowIMEI.clear()

    def on_clicked_main_pb_ShowIMEI(self):
        imei = self.ui.main_editIMEI.text()
        if imei != "":
            self.ui.main_tbShowIMEI.clear()
            info = get_imei_from_csv(app_path, imei)
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\end.wav")
            try:
                self.ui.main_tbShowIMEI.append(f"<p align=\"center\">{info}</p>")
            except Exception as e:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(e))
                msg.setWindowTitle("Ошибка")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Поле ввода пусто")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    #          Geocoding

    def on_clicked_pb_ShowGeoLatLon(self):
        geo_object = self.ui.main_editGeoObject.text()
        if geo_object != "":
            curr_token = None
            self.ui.main_tbShowGeoObjectLatLon.clear()
            try:
                with open((str(app_path) + "\\tokens\\" + token_ocd), "r") as f:
                    curr_token = f.read()
            except Exception as err:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(err))
                msg.setWindowTitle("Ошибка - токен")
                msg.exec_()
            if curr_token != "":                
                try:
                    str_to_tb, limit = GetCoordinates(token=curr_token, text=geo_object)
                    self.ui.main_tbShowGeoObjectLatLon.append(str_to_tb)
                    self.ui.main_tbShowGeoObjectLatLon.moveCursor(QTextCursor.Start)
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                except Exception as e:
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
            else:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Не удалось получить токен")
                msg.setWindowTitle("Уведомление")
                msg.exec_()

    def on_clicked_pb_clearGeoObject(self):
        self.ui.main_editGeoObject.clear()
        self.ui.main_tbShowGeoObjectLatLon.clear()

    def on_clicked_pb_ShowGeoInfo(self):
        geo_lat = self.ui.main_editGeo_Lat.text()
        geo_lon = self.ui.main_editGeo_Lon.text()
        if geo_lat != "" and geo_lon != "":
            self.ui.main_tbShowGeoObjectInfo.clear()
            curr_token = None
            try:
                with open((str(app_path) + "\\tokens\\" + token_ocd), "r") as f:
                    curr_token = f.read()
            except Exception as err:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(str(err))
                msg.setWindowTitle("Ошибка - токен")
                msg.exec_()
            if curr_token != "":
                try:
                    str_to_tb, _ = GetInfoByCoordinates(token=curr_token, latit=geo_lat, longit=geo_lon)
                    self.ui.main_tbShowGeoObjectInfo.append(str_to_tb)
                    self.ui.main_tbShowGeoObjectInfo.moveCursor(QTextCursor.Start)
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                except Exception as e:
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
            else:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Не удалось получить токен")
                msg.setWindowTitle("Уведомление")
                msg.exec_()

    def on_clicked_pb_clearGeoInfo(self):
        self.ui.main_editGeo_Lat.clear()
        self.ui.main_editGeo_Lon.clear()
        self.ui.main_tbShowGeoObjectInfo.clear()

    def on_clicked_pb_ShowBStations(self):
        PREFIX = "https://opencellid.org/cell/getInArea?key="
        PARAM = "&format=json"
        curr_lat = self.ui.main_editLAT_FindBS.text()
        curr_lon = self.ui.main_editLON_FindBS.text()
        curr_radius = self.ui.main_editRadius.text()
        api_result = None
        if curr_lat != "" and curr_lon != "" and curr_radius != "":
            self.ui.tbrwsr_ShowBStations.clear()
            map = folium.Map(location=[float(curr_lat), float(curr_lon)], zoom_start=15)
            position = curr_lat + "," + curr_lon
            loc = Coord.from_str(position)
            curr_token = None
            try:
                with open((str(app_path) + "\\tokens\\" + token_ocd), "r") as f:
                    curr_token = f.read()
                area = float(curr_radius)
                p_max, p_min = loc.square_from_point(area)
                url = PREFIX + curr_token + "&BBOX=" + p_min.to_str() + ',' + p_max.to_str() + PARAM
                api_result = requests.get(url)
                api_result = json.loads(api_result.text)
                if api_result.get("error") == "Daily limit 5000 requests exceeded for your API key":
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Превышен суточный лимит запросов API. Выбран резервный токен")
                    msg.setWindowTitle("Внимание")
                    msg.exec_()
                    try:
                        with open((str(app_path) + "\\tokens\\" + reserve_token_ocd), "r") as f:
                            curr_token = f.read()
                    except:
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                    new_url = PREFIX + curr_token + "&BBOX=" + p_min.to_str() + ',' + p_max.to_str() + PARAM
                    api_result = requests.get(new_url)
                    api_result = json.loads(api_result.text)
                else:
                    pass

                if self.ui.main_check_mapShow.isChecked():
                    folium.Marker(location=[float(curr_lat), float(curr_lon)], popup=("Исходное местоположение"),
                                icon=folium.Icon(color="green", icon="info-sign")).add_to(map)

                if self.ui.cb_ModeBTSShowing.currentIndex() == 0:
                    list_bts = api_result.get("cells")
                    base_dict = {}
                    if list_bts:
                        if len(list_bts) > 0:
                            try:
                                for base in list_bts:
                                    mnc = str(base["mnc"])
                                    if len(mnc) == 1:
                                        mnc = "0" + mnc
                                    base_dict = append_to_dict(base_dict, (str(base["mcc"]), mnc, str(base["radio"]), str(base["lac"]), str(base["cellid"])))
                                string_to_return = return_cool_str(app_path, base_dict)
                                self.ui.tbrwsr_ShowBStations.clear()
                                self.ui.tbrwsr_ShowBStations.append(string_to_return)
                                if self.ui.main_checkBox_sound.isChecked():
                                    playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                            except:
                                self.ui.tbrwsr_ShowBStations.append("<b>Ничего не найдено!</b>")
                        else:
                            if api_result.get("error") == "No cells found":
                                self.ui.tbrwsr_ShowBStations.append("<b>Ничего не найдено!</b>")
                            else:
                                self.ui.tbrwsr_ShowBStations.append("<b>Ничего не найдено!</b>")
                    else:
                        if api_result.get("error") == "No cells found":
                            self.ui.tbrwsr_ShowBStations.append("<b>Ничего не найдено!</b>")
                        else:
                            pass
                elif self.ui.cb_ModeBTSShowing.currentIndex() == 1:

                    string_to_html = "<title>Отчет. Базовые станции</title>"
                    string_to_html += "<big><b>Источник: unwiredlabs.com, сервис: OpenCellId</b></big>"
                    string_to_html += "<br>Информация о ближайших базовых станций ССПР"
                    string_to_html += "<br>Всего найдено: <i>" + str(api_result['count']) + "</i>"
                    string_to_html += "<br>Местоположение: <i>" + position + "</i>"
                    string_to_html += "<br>Радиус: <i>" + curr_radius + "</i>"
                    string_to_html += "<br>Заголовок: №. стандарт, широта, долгота, mcc, nmc, lac, cid"
                    string_to_html += "<br>"
                    cnt = 0
                    for cell in api_result['cells']:
                        cnt = cnt + 1
                        cid = cell['cellid']
                        lat = cell['lat']
                        lon = cell['lon']
                        lac = cell['lac']
                        mcc = cell['mcc']
                        mnc = cell['mnc']
                        radio = cell['radio']
                        string_to_html += "<br>"
                        string_to_html += (str(cnt) + ". " + radio + ", " + str(lat) + ", " + str(lon)
                                        + ", " + str(mcc) + ", " + str(mnc) + ", " + str(lac) + ", " + str(cid))
                        try:
                            if self.ui.main_check_mapShow.isChecked():
                                folium.Marker(location=[float(lat), float(lon)], popup=(str(lat) + ";" + str(lon)),
                                            icon=folium.Icon(color="blue", icon="signal")).add_to(map)
                        except Exception as err_m:
                            print(err_m)
                    try:
                        FileName = app_path + "\\reports\\BSInfo_report_"
                        currDt = datetime.datetime.now()
                        string_time = currDt.strftime('%Y.%m.%d_%H.%M.%S')
                        FileNameMap = app_path + "\\reports\\Map_"
                        FileNameMap += string_time
                        FileName += string_time
                        string_to_message = "Отчет со списком сохранен. Имя:\n"
                        string_to_message += FileName
                        if self.ui.main_check_mapShow.isChecked():
                            string_to_message += "\nКарта создана. Имя:\n"
                            string_to_message += FileNameMap
                        string_to_message += "\nВсего найдено: " + str(api_result['count'])
                        FileNameMap += ".html"
                        FileName += ".html"
                        with open(FileName, "w", encoding='utf-8') as file:
                            file.write(string_to_html)
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                        if self.ui.main_check_mapShow.isChecked():
                            map.save(FileNameMap)
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.NoIcon)
                        msg.setText(string_to_message)
                        msg.setWindowTitle("Сохранение результата")
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                        msg.exec_()
                    except Exception as e:
                        if self.ui.main_checkBox_sound.isChecked():
                            playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText(str(e))
                        msg.setWindowTitle("Ошибка")
                        msg.exec_()
            except:
                if self.ui.main_checkBox_sound.isChecked():
                    playsound(str(app_path) + "\\sources\\sounds\\err.wav")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("При подключении возникли проблемы с токеном")
                msg.setWindowTitle("Ошибка")
                msg.exec_()
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Недостаточно данных!\nПроверьте все поля")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def on_clicked_main_pb_clearShowBStations(self):
        self.ui.main_editLAT_FindBS.clear()
        self.ui.main_editLON_FindBS.clear()
        self.ui.main_editRadius.clear()
        self.ui.tbrwsr_ShowBStations.clear()
        self.ui.main_check_mapShow.setChecked(False)

    def on_clicked_main_pb_clearShowBTSGeo(self):
        self.ui.le_BTSGeo_mcc.clear()
        self.ui.le_BTSGeo_mnc.clear()
        self.ui.le_BTSGeo_lac.clear()
        self.ui.le_BTSGeo_cid.clear()
        self.ui.textBrowser_BTSGeo.clear()

    def on_clicked_main_pb_ShowBTSGeo(self):
        self.ui.textBrowser_BTSGeo.clear()
        mcc = self.ui.le_BTSGeo_mcc.text()
        mnc = self.ui.le_BTSGeo_mnc.text()
        lac = self.ui.le_BTSGeo_lac.text()
        cid = self.ui.le_BTSGeo_cid.text()
        flag_find = False
        if mnc != "" and mcc != "" and lac != "" and cid != "":
            curr_token = None
            try:
                with open((str(app_path) + "\\tokens\\" + token_ocd), "r") as f:
                    curr_token = f.read()
                res = get_coordinates(mcc, mnc, lac, cid, curr_token)
                if res[0]:
                    self.ui.textBrowser_BTSGeo.append("<p align=\"center\"><h4>OpenCellId.org</h4></p>")
                    self.ui.textBrowser_BTSGeo.append(str(res[0]) + "," + str(res[1]))
                    self.ui.textBrowser_BTSGeo.append(str(res[2]))
                    flag_find = True
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                else:
                    pass
            except Exception as e:
                print(e)
            try:
                res = get_coordinates_inikov(mcc, mnc, lac, cid)
                if res[0]:
                    self.ui.textBrowser_BTSGeo.append("<p align=\"center\"><h4>mylnikov.org</h4></p>")
                    self.ui.textBrowser_BTSGeo.append(str(res[0]) + "," + str(res[1]))
                    flag_find = True
                    if self.ui.main_checkBox_sound.isChecked():
                        playsound(str(app_path) + "\\sources\\sounds\\end.wav")
                else:
                    pass
            except:
                pass
            if not flag_find:
                self.ui.textBrowser_BTSGeo.append("<p align=\"center\"><h4>Ничего не найдено!</h4></p>")
        else:
            if self.ui.main_checkBox_sound.isChecked():
                playsound(str(app_path) + "\\sources\\sounds\\err.wav")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Поля ввода пустые")
            msg.setWindowTitle("Ошибка")
            msg.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MyWin()
    main_window.setWindowFlags(QtCore.Qt.Window)
    ico = QtGui.QIcon(app_path + "\\sources\\images\\ico_main.ico")
    main_window.setWindowIcon(ico)
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap(app_path + "\\sources\\images\\splash.jpg"))
    splash.showMessage("Загрузка данных... 0%", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
    splash.show()
    QtWidgets.qApp.processEvents()
    main_window.load_data(splash)
    desktop = QtWidgets.QApplication.desktop()
    main_window.move(desktop.availableGeometry().center() -
                     main_window.rect().center())
    splash.finish(main_window)

    main_window.show()
    sys.exit(app.exec_())
