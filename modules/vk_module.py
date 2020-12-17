import requests
import re
import datetime
import urllib
import urllib.request
from urllib.parse import urlencode
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtCore
import os
from pprint import pprint
import sys

# содержимое файла "tokens/vk_log_pass.txt": {логин пароль client_id} -> разделены пробелом
global_path_to_tok = None
global_path_to_l_p = None
global_path_scr = None
global_code_app = None

def VK_GetAppPath(main_path,path_log_pass, path_tok):
    global global_path_scr
    global global_path_to_tok
    global global_path_to_l_p
    global_path_scr = str(main_path)
    global_path_to_l_p = str(path_log_pass)
    global_path_to_tok = str(path_tok)

def VK_LoadLoginPassword(path):
    with open(str(path), "r") as f:
        currStr = f.read()
        list = currStr.split(" ")
        login = list[0]
        password = list[1]
    return login, password

def ReturnToken():
    global global_path_to_tok
    global global_path_to_l_p
    login, password = VK_LoadLoginPassword(str(global_path_to_l_p))
    access_token = oauth(login=login, password=password, client_id=7430446)
    with open(str(global_path_to_tok), 'w') as f:
        f.write(access_token)
    return access_token

def authentication(login, password, scope):
    session = requests.Session()
    response = session.get('https://m.vk.com')
    url = re.search(r'action="([^\"]+)"', response.text).group(1)
    data = {'email': login, 'pass': password}
    response = session.post(url, data=data)
    return session

def oauth(login = None, password = None, client_id= None, scope=2097151):
    session = authentication(login, password, scope)
    data = {
        'response_type': 'token',
        'client_id': client_id,
        'scope': "friend",
        'redirect_uri': 'https://vk.com/callback',
        'display': 'mobile',
        'v': '5.103',
        'state': '123456'
        }
    response = session.post('https://oauth.vk.com/authorize', data=data)

    if 'access_token' not in response.url:
        url = re.search(r'action="([^\"]+)"', response.text).group(1)
        response = session.get(url)

    try:
        return re.search(r'access_token=([^\&]+)', response.url).group(1)
    except:
        return None

class API(object):
    def __init__(self, token=None, version='5.103', **kwargs):
        self.__token = token
        self.__version = version
        self.__method = kwargs.get('method', '')

    def get_url(self, method=None, **kwargs):

        kwargs.setdefault('v', self.__version)
        if self.__token is not None:
            kwargs.setdefault('access_token', self.__token)
        return 'https://api.vk.com/method/{}?{}'.format(
            method or self.__method, urlencode(kwargs)
        )

    def request(self, method, **kwargs):
        kwargs.setdefault('v', self.__version)
        if self.__token is not None:
            kwargs.setdefault('access_token', self.__token)
        return requests.get(self.get_url(method, **kwargs)).json()

    def __getattr__(self, attr):
        method = ('{}.{}'.format(self.__method, attr)).lstrip('.')
        return API(self.__token, version=self.__version, method=method)

    def __call__(self, **kwargs):
        return self.request(self.__method, **kwargs)

def VK_Search(handler, name, sort_rule, online_stat, age = None, offset = "0"):
    global global_path_to_tok
    global global_path_to_l_p
    count = ""
    sortNum = "1"
    if online_stat == "online":
        online_status = "1"
    elif online_stat == "offline":
        online_status = "0"
    else:
        online_status = "0"

    if sort_rule == "date":
        sortNum = "1"
    elif sort_rule == "popularity":
        sortNum = "0"

    stringFields = "sex, bdate, common_count, city, country, home_town, screen name, about, contacts, domain, followers_count, has_mobile, last_seen, online, screen_name, verified"

    if age == None:
        try:
            response = API.request(handler, method="users.search", q=name, sort=sortNum,
                                   online=online_status, fields=stringFields, count=str(200), offset = str(offset))
        except:
            access_token = ReturnToken()
            session = API(access_token, version="5.103")
            response = API.request(session, method="users.search", q=name, sort=sortNum,
                                   online=online_status, count=str(200), fields=stringFields, offset = str(offset))
    else:
        try:
            response = API.request(handler, method="users.search", q=name, sort=sortNum, age_from=age[0], age_to=age[1],
                                   online=online_status, fields=stringFields, count=str(200), offset = str(offset))
        except:
            access_token = ReturnToken()
            session = API(access_token, version="5.103")
            response = API.request(session, method="users.search", q=name, sort=sortNum, age_from=age[0], age_to=age[1],
                                   online=online_status, fields=stringFields, count=str(200), offset = str(offset))
    model = QStandardItemModel()
    if response.get("response") != None:
        resp = response.get("response")
        countItems = resp.get("count")
        items = resp.get("items")
        if countItems == 0:
            result = "good"
            count = "0"
        else:
            if items != None:
                count_model = 0
                model.setHorizontalHeaderLabels(['имя', 'id', 'ник', 'был(а) в сети', 'пол', 'д.р.', 'город'])
                for it in items:
                    item1 = QStandardItem()
                    item2 = QStandardItem()
                    item3 = QStandardItem()
                    item4 = QStandardItem()
                    item5 = QStandardItem()
                    item6 = QStandardItem()
                    item7 = QStandardItem()
                    id = it.get("id")
                    if id != None:
                        item2.setText(str(id))
                    domain = it.get("domain")
                    if domain != None:
                        item3.setText(str(domain))
                    string_to_item1 = ""
                    f_name = it.get("first_name")
                    if f_name != None:
                        string_to_item1 = f_name
                        string_to_item1 += " "
                        l_name = it.get("last_name")
                        if l_name != None:
                            string_to_item1 += l_name
                    item1.setText(str(string_to_item1))
                    last_seen = it.get("last_seen")
                    string_to_item4 = ""
                    if (last_seen != None) and (last_seen != ""):
                        time_last = last_seen.get("time")
                        value = datetime.datetime.fromtimestamp(time_last)
                        string_time = value.strftime('%Y-%m-%d %H:%M:%S')
                        string_to_item4 = string_time
                    platform = it.get("platform")
                    if platform != None:
                        if platform == 1:
                            string_to_item4 += ", моб. верс."
                        elif platform == 2:
                            string_to_item4 += ", app iPhone"
                        elif platform == 3:
                            string_to_item4 += ", app iPad"
                        elif platform == 4:
                            string_to_item4 += ", app Android"
                        elif platform == 5:
                            string_to_item4 += ", app Win.Phone"
                        elif platform == 6:
                            string_to_item4 += ", app Win.10"
                        elif platform == 7:
                            string_to_item4 += ", web"
                    item4.setText(str(string_to_item4))
                    sex = it.get("sex")
                    if sex != None:
                        if it["sex"] == 2:
                            item5.setText(str("М"))
                        elif it["sex"] == 1:
                            item5.setText(str("Ж"))
                    bday = it.get("bdate")
                    if bday != None:
                        item6.setText(str(bday))
                    string_to_item7 = ""
                    city = it.get("city")
                    if city != None:
                        string_to_item7 = city.get("title")
                        country = it.get("country")
                        if country != None:
                            string_to_item7 += (", " + country.get("title"))
                    item7.setText(str(string_to_item7))
                    item1.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item2.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item3.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item4.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item5.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item6.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item7.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    model.setItem(count_model, 0, item1)
                    model.setItem(count_model, 1, item2)
                    model.setItem(count_model, 2, item3)
                    model.setItem(count_model, 3, item4)
                    model.setItem(count_model, 4, item5)
                    model.setItem(count_model, 5, item6)
                    model.setItem(count_model, 6, item7)
                    #model.appendRow([item1, item2, item3, item4, item5, item6, item7])
                    #model.setItem([item1, item2, item3, item4, item5, item6, item7])
                    count_model += 1

            result = "good"
            count = str(countItems)
    else:
        result = "bad"
        resp2 = response.get("error")
        if resp2 != None:
            err_msg = resp2.get("error_msg")
            if err_msg == "User authorization failed: access_token has expired." or err_msg == "User authorization failed: invalid access_token (4).":
                err_msg += ", повторите запрос"
                os.remove(str(global_path_to_tok))
                access_tok = ReturnToken()
            count = err_msg

    return result, count, model

def VK_SearchGroups(handler, text = None, sort_rule = None, count = None, offset = None):
    global global_path_to_tok
    global global_path_to_l_p
    result = ""
    count_groups = ""
    try:
        response = API.request(handler, method="groups.search", q=text, sort=str(sort_rule), count=str(count), offset = str(offset))
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="groups.search", q=text, sort=str(sort_rule), count=str(count), offset = str(offset))
    model = QStandardItemModel()
    if response.get("response") != None:
        result = "good"
        resp = response.get("response")
        countItems = resp.get("count")
        count_groups = str(countItems)
        items = resp.get("items")
        if countItems == 0:
            result = "good"
            count_groups = "0"
        else:
            if items != None:
                count_model = 0
                model.setHorizontalHeaderLabels(['название', 'id', 'открытое', 'тип', 'ссылка'])
                for it in items:
                    item1 = QStandardItem()
                    item2 = QStandardItem()
                    item3 = QStandardItem()
                    item4 = QStandardItem()
                    item5 = QStandardItem()
                    name = it.get("name")
                    if name != None:
                        item1.setText("   " + name)
                    else:
                        item1.setText("?")
                    id = it.get("id")
                    if id != None:
                        item2.setText(str(id))
                    else:
                        item2.setText("?")
                    is_closed = it.get("is_closed")
                    if is_closed != None:
                        if is_closed == 1:
                            item3.setText("нет")
                        else:
                            item3.setText("да")
                    else:
                        item3.setText("?")
                    type_group = it.get("type")
                    if type_group != None:
                        if type_group == "page":
                            item4.setText("страница")
                        elif type_group == "group":
                            item4.setText("группа")
                    else:
                        item4.setText("?")
                    link = it.get("screen_name")
                    if link != None:
                        string_to_item5 = "https://vk.com/"
                        string_to_item5 += link
                        item5.setText(string_to_item5)
                    else:
                        item5.setText("?")
                    item1.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    item2.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item3.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item4.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item5.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    model.setItem(count_model, 0, item1)
                    model.setItem(count_model, 1, item2)
                    model.setItem(count_model, 2, item3)
                    model.setItem(count_model, 3, item4)
                    model.setItem(count_model, 4, item5)
                    count_model += 1
    else:
        result = "bad"
        resp2 = response.get("error")
        if resp2 != None:
            err_msg = resp2.get("error_msg")
            count_groups = err_msg
            if err_msg == "User authorization failed: access_token has expired." or err_msg == "User authorization failed: invalid access_token (4).":
                count_groups += ", повторите запрос"
                os.remove(str(global_path_to_tok))
                access_tok = ReturnToken()
    return result, count_groups, model

def VK_isMemberInGroup(handler, group_identity = "", user_identity = ""):
    global global_path_to_tok
    global global_path_to_l_p
    result_to_return = ""
    string_to_return = ""
    try:
        response = API.request(handler, method="groups.isMember", group_id=group_identity, user_id=user_identity, extended=1)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="groups.isMember", group_id=group_identity, user_id=user_identity, extended=1)
    resp = response.get("response")
    if resp != None:
        result_to_return = "good"
        member = resp.get("member")
        if member != None:
            if member == 1:
                string_to_return += ("Пользователь id" + user_identity + " состоит в группе")
            elif member == 0:
                string_to_return += ("Пользователь id" + user_identity + " НЕ состоит в группе\n")
                can_invite = resp.get("can_invite")
                if can_invite != None:
                    if can_invite == 1:
                        string_to_return += "Может быть приглашен в группу"
                    else:
                        string_to_return += "НЕ может быть приглашен в группу"
    else:
        if response.get("error") != None:
            res_error = response.get("error")
            result_to_return = "error"
            string_to_return = res_error.get("error_msg")
            if string_to_return == "User authorization failed: access_token has expired." or string_to_return == "User authorization failed: invalid access_token (4).":
                string_to_return += ", повторите запрос"
                os.remove(str(global_path_to_tok))
                access_tok = ReturnToken()
                session = API(access_tok, version="5.103")
                try:
                    response = API.request(session, method="groups.isMember", group_id=group_identity,
                                           user_id=user_identity, extended=1)
                except:
                    access_token = ReturnToken()
                    session = API(access_token, version="5.103")
                    response = API.request(session, method="groups.isMember", group_id=group_identity,
                                           user_id=user_identity, extended=1)
                resp = response.get("response")
                if resp != None:
                    result_to_return = "good"
                    member = resp.get("member")
                    if member != None:
                        if member == 1:
                            string_to_return += ("Пользователь id" + user_identity + " состоит в группе")
                        elif member == 0:
                            string_to_return += ("Пользователь id" + user_identity + " НЕ состоит в группе\n")
                            can_invite = resp.get("can_invite")
                            if can_invite != None:
                                if can_invite == 1:
                                    string_to_return += "Может быть приглашен в группу"
                                else:
                                    string_to_return += "НЕ может быть приглашен в группу"
    return result_to_return, string_to_return

def VK_GetFullInfo(handler, user_id = "440278043", show_friends = True, show_subs = True, show_followers = True, show_all_groups = True, show_wall = True, wall_records = 10):
    global global_path_to_tok
    global global_path_to_l_p
    string_to_return = ""
    string_to_report = ""
    result = ""
    string_error = ""
    if user_id.isdigit():
        result, string_ret, string_to_report = VK_GetUsrInfo(handler, user=user_id)
        string_to_return += string_ret
        string_error = string_ret
        if show_friends:
            string_ret = VK_GetUsrFriends(handler, user=user_id)
            string_to_return += "<p align=\"center\"><h3>Информация о друзьях</h3></p>"
            string_to_report += "<p align=\"center\"><h3>Информация о друзьях</h3></p>"
            string_to_return += string_ret
            string_to_report += string_ret
            if string_ret == "<p align=\"center\">У пользователя нет друзей</p>":
                string_to_return += "<hr color=\"#008000\" size=\"1\" noshade>"
                string_to_report += "<hr color=\"#008000\" size=\"1\" noshade>"
            else:
                string_to_return += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
                string_to_report += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
        if show_followers:
            string_ret = VK_GetUsrFollowers(handler, user=user_id)
            string_to_return += "<p align=\"center\"><h3>Информация о подписчиках</h3></p>"
            string_to_report += "<p align=\"center\"><h3>Информация о подписчиках</h3></p>"
            string_to_return += string_ret
            string_to_report += string_ret
            if string_ret == "<p align=\"center\"><br>У пользователя нет подписчиков</br></p>":
                string_to_return += "<hr color=\"#008000\" size=\"1\" noshade>"
                string_to_report += "<hr color=\"#008000\" size=\"1\" noshade>"
            else:
                string_to_return += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
                string_to_report += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
        if show_subs:
            string_ret = VK_GetUsrSubscriptions(handler, user=user_id)
            string_to_return += "<p align=\"center\"><h3>Информация о подписках</h3></p>"
            string_to_report += "<p align=\"center\"><h3>Информация о подписках</h3></p>"
            string_to_return += string_ret
            string_to_report += string_ret
            if string_ret == "<p align=\"center\">У пользователя нет подписок</p>":
                string_to_return += "<hr color=\"#008000\" size=\"1\" noshade>"
                string_to_report += "<hr color=\"#008000\" size=\"1\" noshade>"
            else:
                string_to_return += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
                string_to_report += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
        if show_all_groups:
            string_ret = VK_GetUserFULLGroups(handler, user=user_id)
            string_to_return += "<p align=\"center\"><h3>Информация о группах</h3></p>"
            string_to_report += "<p align=\"center\"><h3>Информация о группах</h3></p>"
            string_to_return += string_ret
            string_to_report += string_ret
            if string_ret == "<p align=\"center\">У пользователя нет пабликов</p>" or string_ret == "<p align=\"center\">У пользователя нет групп</p>":
                string_to_return += "<hr color=\"#008000\" size=\"1\" noshade>"
                string_to_report += "<hr color=\"#008000\" size=\"1\" noshade>"
            else:
                string_to_return += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
                string_to_report += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
        if show_wall:
            string_ret = VK_GetUsrWall(handler, owner=user_id, count=wall_records)
            string_to_return += "<p align=\"center\"><h3>Стена пользователя</h3></p>"
            string_to_report += "<p align=\"center\"><h3>Стена пользователя</h3></p>"
            string_to_return += string_ret
            string_to_report += string_ret
            string_to_return += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
            string_to_report += "<br><hr color=\"#008000\" size=\"1\" noshade></br>"
    else:
        result = "wrong_args"
    if string_error == "User authorization failed: access_token has expired." or string_error == "User authorization failed: invalid access_token (4).":
        os.remove(str(global_path_to_tok))
        access_tok = ReturnToken()
    return result, string_to_return, string_to_report

def VK_GetUsrInfo(handler, user=None):
    global global_path_to_tok
    global global_path_scr
    global global_path_to_l_p
    result_to_return = ""
    string_to_report = ""
    string_to_return = ""
    photo_return = ""
    stringFields = "sex, bdate, city, books, contacts, exports, career, country, home_town, about, education, counters, connections," \
                   "activities, domain, followers_count, has_mobile, last_seen, online, screen_name, verified, " \
                   "interests, military, maiden_name, movies, music, nickname, occupation, personal, photo_max, photo_max_orig, quotes," \
                   "relation, relatives, schools, site, status, timezone, tv, universities, verified, wall_default"
    try:
        response = API.request(handler, method="users.get", user_id=user, fields=stringFields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="users.get", user_id=user, fields=stringFields)
    resp = response.get("response")
    if resp != None:
        string_to_return += "<p align=\"center\"><h3>Информация о пользователе</h3></p>"
        string_to_report += "<p align=\"center\"><h3>Информация о пользователе</h3></p>"
        result_to_return = "good"
        items = resp[0]
        photo = items.get("photo_max_orig")
        id = items.get("id")
        if id != None:
            if photo != None:
                f_path = str(global_path_scr) + "\\temp\\vk_id" + str(id) + ".jpg"
                if not os.path.exists(f_path):
                    urllib.request.urlretrieve(photo, f_path)
                string_to_return += "<p align=\"center\"><img src=\"" + f_path + "\" title=\"Аватар\"></p>"
        else:
            if photo != None:
                f_path = "temp/last_user_search.jpg"
                if not os.path.exists("temp/last_user_search.jpg"):
                    urllib.request.urlretrieve(photo, f_path)
                string_to_return += "<p align=\"center\"><img src=\"" + f_path + "\" title=\"Аватар\"></p>"

        f_name = items.get("first_name")
        l_name = items.get("last_name")
        if f_name != None and l_name != None:
            string_to_return += ("<b>Пользователь:</b> <big>" + f_name + " " + l_name + "</big> ")
            string_to_report += ("<b>Пользователь:</b> <big>" + f_name + " " + l_name + "</big> ")
        if id != None:
            string_to_return += (", <code>ID:" + str(id) + "</code>")
            string_to_report += (", <code>ID:" + str(id) + "</code>")
        domain = items.get("domain")
        if domain != None:
            string_to_return += ("<br><b>Ссылка:</b> <u>https://vk.com/" + domain + "</u></br>")
            string_to_report += ("<br><b>Ссылка:</b> <u>https://vk.com/" + domain + "</u></br>")
        string_online_status = ""
        are_online = items.get("online")
        if are_online == 1:
            string_online_status = "<br><b>Сейчас в сети</b>"
            are_online_mobile = items.get("online_mobile")
            if (are_online_mobile == 1) or (are_online_mobile == "1"):
                string_online_status += " с мобильного телефона"
            are_online_app = items.get("online_app")
            if (are_online_app != None):
                string_online_status += " из приложения"
        if string_online_status != "":
            string_to_return += string_online_status
            string_to_report += string_online_status
            string_to_return += "\n"
            string_to_report += "\n"
        if are_online != 1:
            last_seen1 = items.get("last_seen")
            if (last_seen1 != None):
                time_last = last_seen1.get("time")
                value = datetime.datetime.fromtimestamp(time_last)
                string_time = value.strftime('%Y-%m-%d %H:%M:%S')
                string_to_return += ("<br><b>Был(а) в сети:</b> " + string_time)
                string_to_report += ("<br><b>Был(а) в сети:</b> " + string_time)
                string_platform = ""
                platform = last_seen1.get("platform")
                if platform == 1:
                    string_platform = "мобильной версии"
                elif platform == 2:
                    string_platform = "приложения на iPhone"
                elif platform == 3:
                    string_platform = "приложения на iPad"
                elif platform == 4:
                    string_platform = "приложения на Android"
                elif platform == 5:
                    string_platform = "приложения на Windows Phone"
                elif platform == 6:
                    string_platform = "приложения на Windows 10"
                elif platform == 7:
                    string_platform = "полной версии сайта"
                string_to_return += (", доступ осуществлялся с " + string_platform + "</br>")
                string_to_report += (", доступ осуществлялся с " + string_platform + "</br>")
        bday = items.get("bdate")
        if bday != None:
            string_to_return += ("<br><b>Дата рождения:</b> " + bday + "</br>")
            string_to_report += ("<br><b>Дата рождения:</b> " + bday + "</br>")
        city = items.get("city")
        if city != None:
            string_to_return += ("<br><b>Проживает:</b> " + city.get("title"))
            string_to_report += ("<br><b>Проживает:</b> " + city.get("title"))
            country = items.get("country")
            if country != None:
                string_to_return += (", " + country.get("title") + "</br>")
                string_to_report += (", " + country.get("title") + "</br>")
        hometown = items.get("home_town")
        if (hometown != None) and (hometown != ""):
            string_to_return += ("<br><b>Родной город:</b> <i>" + hometown + "</i>" + "</br>")
            string_to_report += ("<br><b>Родной город:</b> <i>" + hometown + "</i>" + "</br>")
        counters_dict = items.get("counters")
        if counters_dict != None:
            friends = counters_dict.get("friends")
            string_to_return += ("<p><b>Друзья:</b> <code>" + str(friends) + "</code>")
            string_to_report += ("<p><b>Друзья:</b> <code>" + str(friends) + "</code>")
            subscriptions = counters_dict.get("subscriptions")
            string_to_return += ("<br><b>Подписки:</b> <code>" + str(subscriptions) + "</code></br>")
            string_to_report += ("<br><b>Подписки:</b> <code>" + str(subscriptions) + "</code></br>")
            followers = counters_dict.get("followers")
            string_to_return += ("<br><b>Подписчики:</b> <code>" + str(followers) + "</code></br>")
            string_to_report += ("<br><b>Подписчики:</b> <code>" + str(followers) + "</code></br>")
            groups = counters_dict.get("groups")
            string_to_return += ("<br><b>Группы:</b> <code>" + str(groups) + "</code></br>")
            string_to_report += ("<br><b>Группы:</b> <code>" + str(groups) + "</code></br>")
            pages = counters_dict.get("pages")
            string_to_return += ("<br><b>Паблики:</b> <code>" + str(pages) + "</code></br>")
            string_to_report += ("<br><b>Паблики:</b> <code>" + str(pages) + "</code></br>")
            photos = counters_dict.get("photos")
            string_to_return += ("<br><b>Фото:</b> <code>" + str(photos) + "</code></br>")
            string_to_report += ("<br><b>Фото:</b> <code>" + str(photos) + "</code></br>")
            albums = counters_dict.get("albums")
            string_to_return += ("<br><b>Альбомы:</b> <code>" + str(albums) + "</code></br>")
            string_to_report += ("<br><b>Альбомы:</b> <code>" + str(albums) + "</code></br>")
            audios = counters_dict.get("audios")
            string_to_return += ("<br><b>Аудиозаписи:</b> <code>" + str(audios) + "</code></br>")
            string_to_report += ("<br><b>Аудиозаписи:</b> <code>" + str(audios) + "</code></br>")
            videos = counters_dict.get("videos")
            string_to_return += ("<br><b>Видеозаписи:</b> <code>" + str(videos) + "</code></br></p>")
            string_to_report += ("<br><b>Видеозаписи:</b> <code>" + str(videos) + "</code></br></p>")
        instagram = items.get("instagram")
        facebook = items.get("facebook")
        twitter = items.get("twitter")
        skype = items.get("skype")
        has_soc_seti = False
        if (instagram != None) or (facebook != None) or (twitter != None) or (skype != None):
            has_soc_seti = True
        if has_soc_seti == True:
            string_to_return += ("<br><b>Соцсети:</b></br> ")
            string_to_report += ("<br><b>Соцсети:</b></br> ")
        if instagram != None:
            string_to_return += ("<br><b>instagram:</b> <i>" + instagram + "</i></br>")
            string_to_report += ("<br><b>instagram:</b> <i>" + instagram + "</i></br>")
        if facebook != None:
            string_to_return += ("<br><b>facebook: </b> <i>" + facebook + "</i></br>")
            string_to_report += ("<br><b>facebook: </b> <i>" + facebook + "</i></br>")
        if twitter != None:
            string_to_return += ("<br><b>twitter: </b> <i>" + twitter + "</i></br>")
            string_to_report += ("<br><b>twitter: </b> <i>" + twitter + "</i></br>")
        if skype != None:
            string_to_return += ("<br><b>skype: </b> <i>" + skype + "</i></br>")
            string_to_report += ("<br><b>skype: </b> <i>" + skype + "</i></br>")
        string_to_return += "<p>"
        site = items.get("site")
        if (site != None) and (site != ""):
            string_to_return += ("<br><b>Веб-сайт:</b> <i>" + site + "</i></br>")
            string_to_report += ("<br><b>Веб-сайт:</b> <i>" + site + "</i></br>")
        activities = items.get("activities")
        if (activities != None) and (activities != ""):
            string_to_return += ("<br><b>Деятельность:</b> <i>" + activities + "</i></br>")
            string_to_report += ("<br><b>Деятельность:</b> <i>" + activities + "</i></br>")
        interests = items.get("interests")
        if (interests != None) and (interests != ""):
            string_to_return += ("<br><b>Интересы:</b> <i>" + interests + "</i></br>")
            string_to_report += ("<br><b>Интересы:</b> <i>" + interests + "</i></br>")
        about = items.get("about")
        if (about != None) and (about != ""):
            string_to_return += ("<br><b>О себе:</b> <i>" + about + "</i></br>")
            string_to_report += ("<br><b>О себе:</b> <i>" + about + "</i></br>")
        status = items.get("status")
        if (status != None) and (status != ""):
            string_to_return += ("<br><b>Текст статуса:</b> <i>" + status + "</i></br>")
            string_to_report += ("<br><b>Текст статуса:</b> <i>" + status + "</i></br>")
        verified = items.get("verified")
        if verified == 1:
            string_to_return += "<br><b>Страница верифицирована</b></br>"
            string_to_report += "<br><b>Страница верифицирована</b></br>"
        books = items.get("books")
        if (books != None) and (books != ""):
            string_to_return += ("<br><b>Любимые книги:</b> <i>" + books + "</i></br>")
            string_to_report += ("<br><b>Любимые книги:</b> <i>" + books + "</i></br>")
        movies = items.get("movies")
        if (movies != None) and (movies != ""):
            string_to_return += ("<br><b>Любимые фильмы:</b> <i>" + movies + "</i></br>")
            string_to_report += ("<br><b>Любимые фильмы:</b> <i>" + movies + "</i></br>")
        tv = items.get("tv")
        if (tv != None) and (tv != ""):
            string_to_return += ("<br><b>Любимые телешоу:</b> <i>" + tv + "</i></br>")
            string_to_report += ("<br><b>Любимые телешоу:</b> <i>" + tv + "</i></br>")
        music = items.get("music")
        if (music != None) and (music != ""):
            string_to_return += ("<br><b>Любимая музыка:</b> <i>" + music + "</i></br>")
            string_to_report += ("<br><b>Любимая музыка:</b> <i>" + music + "</i></br>")
        string_to_return += "</p>"
        string_to_report += "</p>"
        string_to_return += "<hr color=\"#008000\" size=\"1\" noshade>"
        string_to_report += "<hr color=\"#008000\" size=\"1\" noshade>"

    else:
        if response.get("error") != None:
            error_response = response.get("error")
            if error_response != None:
                result_to_return = "error"
                string_to_return = error_response.get("error_msg")
                if string_to_return  == "User authorization failed: access_token has expired." or string_to_return == "User authorization failed: invalid access_token (4).":
                    string_to_return += ", повторите запрос"
                    os.remove(str(global_path_to_tok))
                    access_tok = ReturnToken()
    return result_to_return, string_to_return, string_to_report

def VK_GetUsrFriends(handler, user=None):
    global global_path_to_tok
    global global_path_to_l_p
    result_to_return = ""
    stringFields = "sex, bdate, city, country, home_town, contacts, exports, domain, counters, followers_count, online, screen_name"
    try:
        response = API.request(handler, method="friends.get", user_id=str(user), fields=stringFields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="friends.get", user_id=str(user), fields=stringFields)
    if response.get("error"):
        resp1 = response.get("error")
        resp2 = resp1.get("error_msg")
        result_to_return = "<br align=\"center\">Невозможно отобразить друзей пользователя (VK.API: " + resp2 + ")" + "</br>"
        if resp2 == "User authorization failed: access_token has expired." or resp2=="User authorization failed: invalid access_token (4).":
            result_to_return += ", повторите запрос"
            os.remove(str(global_path_to_tok))
    dictFriends = response.get("response")
    if dictFriends != None:
        countFriends = dictFriends.get("count")
        if countFriends == "0":
            result_to_return = "<p align=\"center\">У пользователя нет друзей</p>"
        else:
            itemsFriends = dictFriends.get("items")
            count = 0
            if itemsFriends != None:
                for it in itemsFriends:
                    count += 1
                    f_name = it.get("first_name")
                    id = it.get("id")
                    if f_name != None:
                        l_name = it.get("last_name")
                        if l_name != None:
                            if count == 1:
                                result_to_return += ("<b>" + str(count) + ". " + f_name + " " + l_name + "</b><code>, ID:" + str(id) + "</code>")
                            else:
                                result_to_return += ("<br><b>" + str(count) + ". " + f_name + " " + l_name + "</b><code>, ID:" + str(id) + "</code></br>")
                    string_online_status = ""
                    are_online = it.get("online")
                    if are_online == 1:
                        string_online_status = "<br>Сейчас в сети"
                        are_online_mobile = it.get("online_mobile")
                        if (are_online_mobile == 1) or (are_online_mobile == "1"):
                            string_online_status += " с мобильного телефона"
                            are_online_app = it.get("online_app")
                            if (are_online_app != None):
                                string_online_status += " из приложения"
                    if string_online_status != "":
                        result_to_return += string_online_status
                        result_to_return += "</br>"
                    if are_online != 1:
                        last_seen1 = it.get("last_seen")
                        if (last_seen1 != None):
                            time_last = last_seen1.get("time")
                            value = datetime.datetime.fromtimestamp(time_last)
                            string_time = value.strftime('%Y-%m-%d %H:%M:%S')
                            result_to_return += ("<br>Был(а) в сети: " + string_time)
                            string_platform = ""
                            platform = last_seen1.get("platform")
                            if platform == 1:
                                string_platform = "мобильной версии"
                            elif platform == 2:
                                string_platform = "приложения на iPhone"
                            elif platform == 3:
                                string_platform = "приложения на iPad"
                            elif platform == 4:
                                string_platform = "приложения на Android"
                            elif platform == 5:
                                string_platform = "приложения на Windows Phone"
                            elif platform == 6:
                                string_platform = "приложения на Windows 10"
                            elif platform == 7:
                                string_platform = "полной версии сайта"
                            result_to_return += (", доступ осуществлялся с " + string_platform + "</br>")
                    domain = it.get("domain")
                    if domain != None:
                        result_to_return += ("<br>Ссылка: <i><u>https://vk.com/" + domain + "</u></i></br>")
                    bday = it.get("bdate")
                    if bday != None:
                        result_to_return += ("<br>Дата рождения: " + bday + "</br>")
                    city = it.get("city")
                    if city != None:
                        result_to_return += ("<br>Проживает: " + city.get("title"))
                        country = it.get("country")
                        if country != None:
                            result_to_return += (", " + country.get("title") + "</br>")
    return result_to_return

def VK_GetUsrFollowers(handler, user=None):
    global global_path_to_tok
    global global_path_to_l_p
    result_to_return = ""
    stringFields = "sex, bdate, city, country, home_town, contacts, exports, domain, counters, followers_count, online, screen_name"
    try:
        response = API.request(handler, method="users.getFollowers", user_id=str(user), fields=stringFields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="users.getFollowers", user_id=str(user), fields=stringFields)
    if response.get("error"):
        resp1 = response.get("error")
        resp2 = resp1.get("error_msg")
        result_to_return = "<br align=\"center\">Невозможно отобразить подписчиков пользователя (VK.API: " + resp2 + ")" + "</br>"
        if resp2 == "User authorization failed: access_token has expired." or resp2=="User authorization failed: invalid access_token (4).":
            result_to_return += ", повторите запрос"
            os.remove(str(global_path_to_tok))
            access_tok = ReturnToken()
    dictFollowers = response.get("response")
    if dictFollowers != None:
        countFriends = dictFollowers.get("count")
        if countFriends == "0":
            result_to_return = "<p align=\"center\"><br>У пользователя нет подписчиков</br></p>"
        else:
            itemsFriends = dictFollowers.get("items")
            count = 0
            if itemsFriends != None:
                for it in itemsFriends:
                    count += 1
                    f_name = it.get("first_name")
                    id = it.get("id")
                    if f_name != None:
                        l_name = it.get("last_name")
                        if l_name != None:
                            if count ==1:
                                result_to_return += ("<b>" + str(count) + ". " + f_name + " " + l_name + " </b><code>, ID:" + str(id) + "</code>")
                            else:
                                result_to_return += ("<br><b>" + str(count) + ". " + f_name + " " + l_name + " </b><code>, ID:" + str(id) + "</code></br>")
                    string_online_status = ""
                    are_online = it.get("online")
                    if are_online == 1:
                        string_online_status = "<br>Сейчас в сети"
                        are_online_mobile = it.get("online_mobile")
                        if (are_online_mobile == 1) or (are_online_mobile == "1"):
                            string_online_status += " с мобильного телефона"
                            are_online_app = it.get("online_app")
                            if (are_online_app != None):
                                string_online_status += " из приложения"
                    if string_online_status != "":
                        result_to_return += string_online_status
                        result_to_return += "</br>"
                    if are_online != 1:
                        last_seen1 = it.get("last_seen")
                        if (last_seen1 != None):
                            time_last = last_seen1.get("time")
                            value = datetime.datetime.fromtimestamp(time_last)
                            string_time = value.strftime('%Y-%m-%d %H:%M:%S')
                            result_to_return += ("<br>Был(а) в сети: " + string_time)
                            string_platform = ""
                            platform = last_seen1.get("platform")
                            if platform == 1:
                                string_platform = "мобильной версии"
                            elif platform == 2:
                                string_platform = "приложения на iPhone"
                            elif platform == 3:
                                string_platform = "приложения на iPad"
                            elif platform == 4:
                                string_platform = "приложения на Android"
                            elif platform == 5:
                                string_platform = "приложения на Windows Phone"
                            elif platform == 6:
                                string_platform = "приложения на Windows 10"
                            elif platform == 7:
                                string_platform = "полной версии сайта"
                            result_to_return += (", доступ осуществлялся с " + string_platform + "</br>")
                    domain = it.get("domain")
                    if domain != None:
                        result_to_return += ("<br>Ссылка: <i><u>https://vk.com/" + domain + "</u></i></br>")
                    bday = it.get("bdate")
                    if bday != None:
                        result_to_return += ("<br>Дата рождения: " + bday + "</br>")
                    city = it.get("city")
                    if city != None:
                        result_to_return += ("<br>Проживает: " + city.get("title"))
                        country = it.get("country")
                        if country != None:
                            result_to_return += (", " + country.get("title") + "</br>")
    return result_to_return

def VK_GetUsrSubscriptions(handler, user=None):
    global global_path_to_tok
    global global_path_to_l_p
    result_to_return = ""
    stringFields = "sex, bdate, city, country, home_town, contacts, exports, domain, counters, followers_count, online, screen_name"
    try:
        response = API.request(handler, method="users.getSubscriptions", user_id=str(user), fields=stringFields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="users.getSubscriptions", user_id=str(user), fields=stringFields)
    if response.get("error") != None:
        resp1 = response.get("error")
        resp2 = resp1.get("error_msg")
        result_to_return = "<br align=\"center\">Невозможно отобразить подписки (VK.API: " + resp2 + ")" + "</br>"
        if resp2 == "User authorization failed: access_token has expired." or resp2=="User authorization failed: invalid access_token (4).":
            result_to_return += ", повторите запрос"
            os.remove(str(global_path_to_tok))
            access_tok = ReturnToken()
    dictSubs2 = response.get("response")
    if dictSubs2 != None:
        dictSubs = dictSubs2.get("users")
        if dictSubs != None:
            countFriends = dictSubs.get("count")
            if countFriends == 0:
                result_to_return = "<p align=\"center\">У пользователя нет подписок</p>"
            else:
                itemsFriends = dictSubs.get("items")
                if itemsFriends != None:
                    if len(itemsFriends) != 0:
                        result_to_return += "Будет выведен <b>список</b> id <b>пользователей</b>, на которых подписан пользователь.<br>Публичные <b>страницы проигнорированы.</b></br>"
                        result_to_return += ("<br><b>Всего:</b> <code><u>" + str(dictSubs.get("count")) + "</u></code></br>")
                        count_end = dictSubs.get("count")  # дает сколько всего, больше 1000 в массив не попадает
                        if dictSubs.get("count") > 1000:
                            count_end = 1000
                            result_to_return += ("<br><b>Выведено:</b> <code><u>" + "1000" + "</u></code></br>")
                        result_to_return += "<br> </br>"
                        for i in range(0, count_end):
                            if i==0:
                                result_to_return += ("<code>" + str(itemsFriends[i]) + "</code>")
                            else:
                                result_to_return += (", <code>" + str(itemsFriends[i]) + "</code>")
    return result_to_return

def VK_GetUserFULLGroups(handler, user=None):
    result_to_return = ""
    res1 = VK_GetUserGroups(handler, user=user, filters="publics", count=1000)
    res2 = VK_GetUserGroups(handler, user=user, filters="groups", count=1000)
    result_to_return += res1
    result_to_return += res2
    return result_to_return

def VK_GetUserGroups(handler, user = None, filters = "z", count = None):
    global global_path_to_tok
    global global_path_to_l_p
    string_to_return = ""
    filtration = filters
    response = None
    if filtration == "publics":
        try:
            response = API.request(handler, method="groups.get", user_id = str(user), filter = filtration, extended = "1", count = str(count), v="5.103")
        except:
            access_token = ReturnToken()
            session = API(access_token, version="5.103")
            response = API.request(session, method="groups.get", filter = filtration, extended = "1", user_id = str(user), count = str(count), v="5.103")
    elif filtration == "groups":
        try:
            response = API.request(handler, method="groups.get", user_id = str(user), filter = filtration, extended = "1", count = str(count), v="5.103")
        except:
            access_token = ReturnToken()
            session = API(access_token, version="5.103")
            response = API.request(session, method="groups.get", user_id = str(user), filter = filtration, extended = "1", count = str(count), v="5.103")
    if response.get("error") != None:
        resp1 = response.get("error")
        resp2 = resp1.get("error_msg")
        if filtration == "publics":
            string_to_return = "<br align=\"center\">Невозможно отобразить паблики (VK.API: " + resp2 + ")" + "</br>"
        elif filtration == "groups":
            string_to_return = "<br align=\"center\">Невозможно отобразить группы (VK.API: " + resp2 + ")" + "</br>"
        if resp2 == "User authorization failed: access_token has expired." or resp2 == "User authorization failed: invalid access_token (4).":
            string_to_return += ", повторите запрос"
            #path = os.path.join(os.path.abspath(os.path.dirname(__file__)), global_path_to_tok)
            os.remove(str(global_path_to_tok))
            access_tok = ReturnToken()
    resp = response.get("response")
    if resp != None:
        countItems = resp.get("count")
        if countItems == 0:
            if filtration == "publics":
                string_to_return = "<p align=\"center\">У пользователя нет пабликов</p>"
            elif filtration == "groups":
                string_to_return = "<p align=\"center\">У пользователя нет групп</p>"
        else:
            items = resp.get("items")
            count_group = 0
            if items != None:
                if filtration == "publics":
                    string_to_return += "<p align=\"center\"><big> Паблики пользователя: </big></p>"
                elif filtration == "groups":
                    string_to_return += "<p align=\"center\"><big> Группы пользователя: </big></p>"
                for it in items:
                    count_group += 1
                    name = it.get("name")
                    id = it.get("id")
                    if name != None and id != None:
                        if count_group == 1:
                            string_to_return += ("<b>" + str(count_group) + ". " + name + "</b><code>, ID:" + str(id) + "</code>")
                        else:
                            string_to_return += ("<br><b>" + str(count_group) + ". " + name + " </b><code>, ID:" + str(id) + "</code></br>")
                    is_closed = it.get("is_closed")
                    if is_closed != None:
                        if is_closed == 1:
                            string_to_return += ("<br>Закрытое сообщество</br>")
                        elif is_closed == 0:
                            string_to_return += ("<br>Открытое сообщество</br>")
                    link = it.get("screen_name")
                    if link != None:
                        string_to_return += ("<br>Ссылка: <u><i>https://vk.com/" + link + "</i></u></br>")
                    foto = it.get("photo_200")
                    if foto != None:
                        string_to_return += ("<br>Аватар группы (200-pix): <u><i>" + foto + "</i></u></br>")
    return string_to_return

def VK_GetUsrWall(handler, owner = None, count = None):
    global global_path_to_tok
    global global_path_to_l_p
    user = owner
    string_to_return = ""
    domain_user = VK_GetUsrDomain(handler, owner = user)
    try:
        response = API.request(handler, method="wall.get", domain=domain_user, extended="1", count=str(count), v="5.103")
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="wall.get", domain=domain_user, extended="1", count=str(count), v="5.103")
    error_response = response.get("error")
    if error_response != None:
        resp = error_response.get("error_msg")
        string_to_return = "<br align=\"center\">Невозможно отобразить стену (VK.API: " + resp + ")" + "</br>"
        if resp == "User authorization failed: access_token has expired." or resp == "User authorization failed: invalid access_token (4).":
            string_to_return += ", повторите запрос"
            os.remove(str(global_path_to_tok))
            access_tok = ReturnToken()
    rresponse = response.get("response")
    if rresponse != None:
        dictRecords = rresponse.get("items")
        if dictRecords != None:
            for it in dictRecords:
                string_to_return += "<p>"
                Date2 = it.get("date")
                Date = datetime.datetime.fromtimestamp(Date2)
                string_to_return += ("<br>Дата публикации: " + Date.strftime('%Y-%m-%d %H:%M:%S') + "</br>")
                FromId = it.get("from_id")
                id_owner = ""
                if FromId != None:
                    StringFrom = "<br>Отправитель: "
                    dictProfiles = rresponse.get("profiles")
                    if dictProfiles != None:
                        for itemProfile in dictProfiles:
                            if FromId == itemProfile.get("id"):
                                StringFrom += "<big>"
                                StringFrom += itemProfile.get("first_name")
                                StringFrom += " "
                                StringFrom += itemProfile.get("last_name")
                                StringFrom += "</big> ,<code>ID:"
                                id_owner = str(FromId)
                                StringFrom += str(FromId)
                                StringFrom += "</code>"
                                StringFrom += "<br>Ссылка: <i>https://vk.com/"
                                StringFrom += itemProfile.get("screen_name")
                                StringFrom += "</i></br>"
                                if itemProfile.get("photo_100") != "https://vk.com/images/camera_100.png?ava=1":
                                    StringFrom += "\n"
                                    StringFrom += "<br>Аватар: <i>"
                                    StringFrom += itemProfile.get("photo_100")
                                    StringFrom += "</i></br>"
                                string_to_return += StringFrom

                    dictGroups = rresponse.get("groups")
                    if dictGroups != None:
                        for itemGroup in dictGroups:
                            if FromId == itemGroup.get("id"):
                                StringFrom += "<big>Название сообщества: "
                                StringFrom += itemGroup.get("name")
                                StringFrom += "</big> ,<code>ID:"
                                StringFrom += str(FromId)
                                StringFrom += "</code>"
                                StringFrom += "<br>Ссылка: <i>https://vk.com/"
                                StringFrom += itemGroup.get("screen_name")
                                StringFrom += "</i></br>"
                                if itemGroup.get("photo_100") != "https://vk.com/images/camera_100.png?ava=1":
                                    StringFrom += "\n"
                                    StringFrom += "<br>Аватар: <i>"
                                    StringFrom += itemGroup.get("photo_100")
                                    StringFrom += "</i></br>"
                                string_to_return += StringFrom

                IdRecord = it.get("id")
                if IdRecord != None:
                    string_to_return += ("<br>Id записи: <code>" + id_owner + "_" + str(IdRecord) + "</code></br>")
                PostType = it.get("post_type")
                if PostType != None:
                    string_to_return += ("<br>Тип записи: " + str(PostType) + "</br>")
                LikesCount = it.get("likes")
                if LikesCount != None:
                    Likes = LikesCount.get("count")
                    string_to_return += ("<br>Понравилось (лайки): <code>" + str(Likes) + "</code></br>")
                RepostsCount = it.get("reposts")
                if RepostsCount != None:
                    Reposts = RepostsCount.get("count")
                    string_to_return += ("<br>Поделились (репосты): <code>" + str(Reposts) + "</code></br>")
                Text = it.get("text")
                if Text != None and Text != "":
                    if len(Text) > 150:
                        new_Text = Text[0:150]
                        string_to_return += (
                                    "<br>Текст (сообщение): <b>\"" + new_Text + "... \"</b> (длина текста: " + str(
                                len(Text)) + " символов)</br>")
                    else:
                        string_to_return += ("<br>Текст (сообщение): <b>\"" + str(Text) + "\"</b></br>")
                attach = it.get("attachments")
                if attach != None:
                    if attach != 0:
                        string_to_return += ("<br><big>Присутствуют вложения, количество: <code>" + str(len(attach)) + "</code></big></br>")
                    count_attach = 0
                    for at_it in attach:
                        count_attach += 1
                        StringAttach = ("<br>" + str(count_attach) + ". <u>")
                        type_at = at_it.get("type")
                        if type_at == "photo":
                            StringAttach += "Изображение"
                            StringAttach += "</u>, "
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                photo_id = attachment.get("id")
                                if photo_id != None:
                                    StringAttach += "photo_id: "
                                    StringAttach += str(photo_id)
                                date_attach = attachment.get("date")
                                if date_attach != None:
                                    value = datetime.datetime.fromtimestamp(date_attach)
                                    StringAttach += ", дата: "
                                    StringAttach += value.strftime('%Y-%m-%d %H:%M:%S')
                                size_dict = attachment.get("sizes")
                                if size_dict != None:
                                    width = 0
                                    image = ""
                                    for item_size in size_dict:
                                        if item_size.get("width") > width:
                                            width = item_size.get("width")
                                            image = item_size.get("url")
                                    StringAttach += ", url: <i>"
                                    StringAttach += image
                                    StringAttach += "</i>"
                        if type_at == "video":
                            StringAttach += "Видеозапись"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += ("</u> \"" + title + "\", ")
                                date_attach = attachment.get("date")
                                if date_attach != None:
                                    value = datetime.datetime.fromtimestamp(date_attach)
                                    StringAttach += "date: "
                                    StringAttach += value.strftime('%Y-%m-%d %H:%M:%S')
                                duration = attachment.get("duration")
                                if duration != None:
                                    StringAttach += (", " + str(duration) + " сек.")
                                description = attachment.get("description")
                                if description != None and description != "":
                                    StringAttach += (", описание: <i>\"" + description + "\"</i>")
                        if type_at == "audio":
                            StringAttach += "Аудиозапись"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                artist = attachment.get("artist")
                                if artist != None:
                                    StringAttach += ("</u> \"" + artist + " - ")
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (title + "\", ")
                                date_attach = attachment.get("date")
                                if date_attach != None:
                                    value = datetime.datetime.fromtimestamp(date_attach)
                                    StringAttach += "дата: "
                                    StringAttach += value.strftime('%Y-%m-%d %H:%M:%S')
                        if type_at == "doc":
                            StringAttach += "Документ</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (" - <u>\"" + title + "\"</u>, ")
                                type = attachment.get("type")
                                if type != None:
                                    if type == 1:
                                        StringAttach += ("текстовый документ")
                                    elif type == 2:
                                        StringAttach += ("архив")
                                    elif type == 3:
                                        StringAttach += ("gif")
                                    elif type == 4:
                                        StringAttach += ("изображение")
                                    elif type == 5:
                                        StringAttach += ("аудио")
                                    elif type == 6:
                                        StringAttach += ("видео")
                                    elif type == 7:
                                        StringAttach += ("электронная книга")
                                    elif type == 8:
                                        StringAttach += ("тип неизвестен")
                                size_document = attachment.get("size")
                                if size_document != None:
                                    StringAttach += (", ")
                                    size_doc = float(size_document)
                                    size_kb = size_doc / 1024
                                    size_kb_n = str(format(size_kb, ".2f"))
                                    size_mb = size_kb / 1024
                                    size_mb_n = str(format(size_mb, ".2f"))
                                    if size_mb > 1:
                                        StringAttach += (size_mb_n + " Мбайт")
                                    else:
                                        StringAttach += (size_kb_n + " Кбайт")
                                url_doc = attachment.get("url")
                                if url_doc != None:
                                    StringAttach += (", ссылка: <i>" + url_doc + "</i>")
                        if type_at == "graffiti":
                            StringAttach += "Граффити</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                author = attachment.get("owner_id")
                                if author != None:
                                    StringAttach += (", автор: " + author)
                                photo_original = attachment.get("photo_604")
                                if photo_original != None:
                                    StringAttach += (", url: <u>" + photo_original + "</u>")
                        if type_at == "link":
                            StringAttach += "Ссылка</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (" - название: " + title)
                                url = attachment.get("url")
                                if url != None:
                                    StringAttach += (", url: <u>" + url + "</u>")
                                description = attachment.get("description")
                                if description != None:
                                    StringAttach += (", описание: <u>" + description + "</u>")
                        if type_at == "note":
                            StringAttach += "Заметка</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (" - заголовок: " + title)
                                text = attachment.get("text")
                                if text != None:
                                    StringAttach += (", текст: " + text)
                                view_url = attachment.get("view_url")
                                if view_url != None:
                                    StringAttach += (", url: <i>" + view_url + "</i>")
                        if type_at == "poll":
                            StringAttach += "Опрос</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                question = attachment.get("question")
                                if question != None:
                                    StringAttach += (" - тема: " + question)
                        if type_at == "page":
                            StringAttach += "Вики-страница</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (" - название: " + title)
                        if type_at == "album":
                            StringAttach += "Альбом с фото</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (" - название: " + title)
                                size = attachment.get("size")
                                if size != None:
                                    StringAttach += (", количество: <size>" + str(size) + "</size>")
                                description = attachment.get("description")
                                if description != None:
                                    StringAttach += (", описание: <u>" + description + "</u>")
                                owner = attachment.get("owner_id")
                                if owner != None:
                                    StringAttach += (", владелец: <u>" + owner + "</u>")
                        if type_at == "market":
                            StringAttach += "Товар</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                title = attachment.get("title")
                                if title != None:
                                    StringAttach += (" - название: " + title)
                                description = attachment.get("description")
                                if description != None:
                                    StringAttach += (", описание: " + description)
                        if type_at == "market_album":
                            StringAttach += "Подборка товаров</u>"
                        if type_at == "sticker":
                            StringAttach += "Стикер</u>"
                        if type_at == "pretty_cards":
                            StringAttach += "Карточки</u>"
                        if type_at == "event":
                            StringAttach += "Встреча</u>"
                            attachment = at_it.get(type_at)
                            if attachment != None:
                                address = attachment.get("address")
                                if address != None:
                                    StringAttach += (" - адрес: " + address)
                                time = attachment.get("time")
                                if time != None:
                                    value = datetime.datetime.fromtimestamp(time)
                                    StringAttach += ", дата: <i>"
                                    StringAttach += (value.strftime('%Y-%m-%d %H:%M:%S') + "</i>")
                        string_to_return += StringAttach
                copy_history = it.get("copy_history")
                if copy_history != None:
                    string_to_return += "<br><u><big>Запись является репостом, оригинал:</big></u></br>"
                    iter_hist = copy_history[0]
                    Date3 = iter_hist.get("date")
                    Date4 = datetime.datetime.fromtimestamp(Date3)
                    string_to_return += ("<br>Дата публикации: " + Date4.strftime('%Y-%m-%d %H:%M:%S') + "</br>")
                    FromIdOriginal_int = iter_hist.get("from_id")
                    if FromIdOriginal_int != None:
                        FromIdOriginal_str = str(FromIdOriginal_int)
                        FromIdOriginal = FromIdOriginal_str[1:]
                        StringFromOrig = "<br>Отправитель: "
                        dictProfilesOrig = rresponse.get("profiles")
                        if dictProfilesOrig != None:
                            for itemProfileOrig in dictProfilesOrig:
                                item_id = itemProfileOrig.get("id")
                                if FromIdOriginal == str(item_id):
                                    StringFromOrig += "<big>"
                                    StringFromOrig += itemProfileOrig.get("first_name")
                                    StringFromOrig += " "
                                    StringFromOrig += itemProfileOrig.get("last_name")
                                    StringFromOrig += "</big> ,<code>ID:"
                                    StringFromOrig += FromIdOriginal
                                    StringFromOrig += "</code>"
                                    StringFromOrig += "<br>Ссылка: <i>https://vk.com/"
                                    StringFromOrig += itemProfileOrig.get("screen_name")
                                    StringFromOrig += "</i></br>"
                                    if itemProfileOrig.get("photo_100") != "https://vk.com/images/camera_100.png?ava=1":
                                        StringFromOrig += "\n"
                                        StringFromOrig += "<br>Аватар: <i>"
                                        StringFromOrig += itemProfileOrig.get("photo_100")
                                        StringFromOrig += "</i></br>"
                                    string_to_return += StringFromOrig

                        dictGroupsOrig = rresponse.get("groups")
                        if dictGroupsOrig != None:
                            for itemGroup in dictGroupsOrig:
                                item_id = itemGroup.get("id")
                                item_id_str = str(item_id)
                                if FromIdOriginal == item_id_str:
                                    StringFromOrig += "<big> "
                                    StringFromOrig += itemGroup.get("name")
                                    StringFromOrig += "</big>, <code>ID:"
                                    StringFromOrig += FromIdOriginal
                                    StringFromOrig += "</code>"
                                    StringFromOrig += "<br>Ссылка: <i>https://vk.com/"
                                    StringFromOrig += itemGroup.get("screen_name")
                                    StringFromOrig += "</i></br>"
                                    if itemGroup.get("photo_100") != "https://vk.com/images/camera_100.png?ava=1":
                                        StringFromOrig += "\n"
                                        StringFromOrig += "<br>Аватар: <i>"
                                        StringFromOrig += itemGroup.get("photo_100")
                                        StringFromOrig += "</i></br>"
                                    string_to_return += StringFromOrig

                    LikesCount = iter_hist.get("likes")
                    if LikesCount != None:
                        Likes = LikesCount.get("count")
                        string_to_return += ("<br>Понравилось (лайки): <code>" + str(Likes) + "</code></br>")
                    RepostsCount = iter_hist.get("reposts")
                    if RepostsCount != None:
                        Reposts = RepostsCount.get("count")
                        string_to_return += ("<br>Поделились (репосты): <code>" + str(Reposts) + "</code></br>")
                    Text = iter_hist.get("text")
                    if Text != None and Text != "":
                        if len(Text) > 150:
                            new_Text = Text[0:150]
                            string_to_return += ("<br>Текст (сообщение): <b>\"" + new_Text + "... \"</b> (длина текста: " + str(len(Text)) + " символов)</br>")
                        else:
                            string_to_return += ("<br>Текст (сообщение): <b>\"" + str(Text) + "\"</b></br>")
                    attach_orig = iter_hist.get("attachments")
                    if attach_orig != None:
                        if attach_orig != 0:
                            string_to_return += ("<br><big>Присутствуют вложения, количество: <code>" + str(len(attach_orig)) + "</code></big></br>")
                        count_attach_orig = 0
                        for at_it_orig in attach_orig:
                            count_attach_orig += 1
                            StringAttachOrig = ("<br>" + str(count_attach_orig) + ". <u>")
                            type_at_o = at_it_orig.get("type")
                            if type_at_o == "photo":
                                StringAttachOrig += "Изображение"
                                StringAttachOrig += "</u>, "
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    photo_id = attachment_orig.get("id")
                                    if photo_id != None:
                                        StringAttachOrig += "photo_id: "
                                        StringAttachOrig += str(photo_id)
                                    date_attach = attachment_orig.get("date")
                                    if date_attach != None:
                                        value = datetime.datetime.fromtimestamp(date_attach)
                                        StringAttachOrig += ", дата: "
                                        StringAttachOrig += value.strftime('%Y-%m-%d %H:%M:%S')
                                    size_dict_orig = attachment_orig.get("sizes")
                                    if size_dict_orig != None:
                                        width = 0
                                        image = ""
                                        for item_size_o in size_dict_orig:
                                            if item_size_o.get("width") > width:
                                                width = item_size_o.get("width")
                                                image = item_size_o.get("url")
                                        StringAttachOrig += ", url: <i>"
                                        StringAttachOrig += image
                                        StringAttachOrig += "</i>"
                            if type_at_o == "video":
                                StringAttachOrig += "Видеозапись"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    title = attachment_orig.get("title")
                                    if title != None:
                                        StringAttachOrig += ("</u> \"" + title + "\", ")
                                    date_attach = attachment_orig.get("date")
                                    if date_attach != None:
                                        value = datetime.datetime.fromtimestamp(date_attach)
                                        StringAttachOrig += "дата: "
                                        StringAttachOrig += value.strftime('%Y-%m-%d %H:%M:%S')
                                    duration_or = attachment_orig.get("duration")
                                    if duration_or != None:
                                        StringAttachOrig += (", " + str(duration_or) + " сек.")
                                    description_orig = attachment_orig.get("description")
                                    if description_orig != None and description_orig != "":
                                        StringAttachOrig += (", описание: \"<i>" + description_orig + "</i>\"")
                            if type_at_o == "audio":
                                StringAttachOrig += "Аудиозапись"
                                attachment = type_at_o.get(type_at_o)
                                if attachment != None:
                                    artist = attachment.get("artist")
                                    if artist != None:
                                        StringAttachOrig += ("</u> \"" + artist + " - ")
                                    title = attachment.get("title")
                                    if title != None:
                                        StringAttachOrig += (title + "\", ")
                                    date_attach = attachment.get("date")
                                    if date_attach != None:
                                        value = datetime.datetime.fromtimestamp(date_attach)
                                        StringAttachOrig += "дата: "
                                        StringAttachOrig += value.strftime('%Y-%m-%d %H:%M:%S')
                            if type_at_o == "doc":
                                StringAttachOrig += "Документ</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    title = attachment_orig.get("title")
                                    if title != None:
                                        StringAttachOrig += (" - <u>\"" + title + "\"</u>, ")
                                    type = attachment_orig.get("type")
                                    if type != None:
                                        if type == 1:
                                            StringAttachOrig += ("текстовый документ")
                                        elif type == 2:
                                            StringAttachOrig += ("архив")
                                        elif type == 3:
                                            StringAttachOrig += ("gif")
                                        elif type == 4:
                                            StringAttachOrig += ("изображение")
                                        elif type == 5:
                                            StringAttachOrig += ("аудио")
                                        elif type == 6:
                                            StringAttachOrig += ("видео")
                                        elif type == 7:
                                            StringAttachOrig += ("электронная книга")
                                        elif type == 8:
                                            StringAttachOrig += ("тип неизвестен")
                                    size_document = attachment_orig.get("size")
                                    if size_document != None:
                                        StringAttachOrig += (", ")
                                        size_doc = float(size_document)
                                        size_kb = size_doc / 1024
                                        size_kb_n = str(format(size_kb, ".2f"))
                                        size_mb = size_kb / 1024
                                        size_mb_n = str(format(size_mb, ".2f"))
                                        if size_mb > 1:
                                            StringAttachOrig += (size_mb_n + " Мбайт")
                                        else:
                                            StringAttachOrig += (size_kb_n + " Кбайт")
                                    url_doc = attachment_orig.get("url")
                                    if url_doc != None:
                                        StringAttachOrig += (", ссылка: <i>" + url_doc + "</i>")
                            if type_at_o == "graffiti":
                                StringAttachOrig += "Граффити</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    author = attachment_orig.get("owner_id")
                                    if author != None:
                                        StringAttachOrig += (", автор: " + author)
                                    photo_original = attachment_orig.get("photo_604")
                                    if photo_original != None:
                                        StringAttachOrig += (", url: <u>" + photo_original + "</u>")
                            if type_at_o == "link":
                                StringAttachOrig += "Ссылка</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    title = attachment_orig.get("title")
                                    if title != None:
                                        StringAttachOrig += (" - название: " + title)
                                    url = attachment_orig.get("url")
                                    if url != None:
                                        StringAttachOrig += (", url: <u>" + url + "</u>")
                                    description = attachment_orig.get("description")
                                    if description != None:
                                        StringAttachOrig += (", описание: <u>" + description + "</u>")
                            if type_at_o == "note":
                                StringAttachOrig += "Заметка</u>"
                                attachment = at_it_orig.get(type_at_o)
                                if attachment != None:
                                    title = attachment.get("title")
                                    if title != None:
                                        StringAttachOrig += (" - заголовок: " + title)
                                    text = attachment.get("text")
                                    if text != None:
                                        StringAttachOrig += (", текст: " + text)
                                    view_url = attachment.get("view_url")
                                    if view_url != None:
                                        StringAttachOrig += (", url: <i>" + view_url + "</i>")
                            if type_at_o == "poll":
                                StringAttachOrig += "Опрос</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    question = attachment_orig.get("question")
                                    if question != None:
                                        StringAttachOrig += (" - тема: " + question)
                            if type_at_o == "page":
                                StringAttachOrig += "Вики-страница</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    title = attachment_orig.get("title")
                                    if title != None:
                                        StringAttachOrig += (" - название: " + title)
                            if type_at_o == "album":
                                StringAttachOrig += "Альбом с фото</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    title = attachment_orig.get("title")
                                    if title != None:
                                        StringAttachOrig += (" - название: " + title)
                                    size = attachment_orig.get("size")
                                    if size != None:
                                        StringAttachOrig += (", количество: <size>" + str(size) + "</size>")
                                    description = attachment_orig.get("description")
                                    if description != None:
                                        StringAttachOrig += (", описание: <u>" + description + "</u>")
                                    owner = attachment_orig.get("owner_id")
                                    if owner != None:
                                        StringAttachOrig += (", владелец: <u>" + owner + "</u>")
                            if type_at_o == "market":
                                StringAttachOrig += "Товар</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    title = attachment_orig.get("title")
                                    if title != None:
                                        StringAttachOrig += (" - название: " + title)
                                    description = attachment_orig.get("description")
                                    if description != None:
                                        StringAttachOrig += (", описание: " + description)
                            if type_at_o == "market_album":
                                StringAttachOrig += "Подборка товаров</u>"
                            if type_at_o == "sticker":
                                StringAttachOrig += "Стикер</u>"
                            if type_at_o == "pretty_cards":
                                StringAttachOrig += "Карточки</u>"
                            if type_at_o == "event":
                                StringAttachOrig += "Встреча</u>"
                                attachment_orig = at_it_orig.get(type_at_o)
                                if attachment_orig != None:
                                    address = attachment_orig.get("address")
                                    if address != None:
                                        StringAttachOrig += (" - адрес: " + address)
                                    time = attachment_orig.get("time")
                                    if time != None:
                                        value = datetime.datetime.fromtimestamp(time)
                                        StringAttachOrig += ", дата: <i>"
                                        StringAttachOrig += (value.strftime('%Y-%m-%d %H:%M:%S') + "</i>")
                            string_to_return += StringAttachOrig
                string_to_return += "</p>"

    return string_to_return

def VK_GetUsrDomain(handler, owner = None):
    domain_return = None
    stringFields = "domain"
    try:
        response = API.request(handler, method="users.get", user_id=owner, fields=stringFields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="users.get", user_id=owner, fields=stringFields)
    resp = response.get("response")
    rsp = resp[0]
    domain = rsp.get("domain")
    if domain != None:
        domain_return = domain
    return domain_return

def VK_MakeDataForDiagrams(handler, user = None):
    global global_path_to_tok
    global global_path_to_l_p
    result_to_return = ""
    res = {'sex':[], 'age': [], 'city': [], 'country': []}
    stringFields = "sex, bdate, city, country, home_town"
    curr_year = datetime.datetime.now().year
    try:
        response = API.request(handler, method="friends.get", user_id=str(user), fields=stringFields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="friends.get", user_id=str(user), fields=stringFields)
    if response.get("error"):
        resp1 = response.get("error")
        resp2 = resp1.get("error_msg")
        result_to_return = "<p align=\"center\"><h2>Невозможно отобразить друзей пользователя</h2></p>"
        if resp2 == "User authorization failed: access_token has expired." or resp2 == "User authorization failed: invalid access_token (4).":
            result_to_return = "<p align=\"center\"><h2>Повторите запрос, нужно обновить токен</h2></p>"
            os.remove(str(global_path_to_tok))
    dictFriends = response.get("response")
    if dictFriends != None:
        count = dictFriends.get("count")
        if count != None:
            result_to_return = "<p align=\"center\"><b>Выборка сделана, количество друзей: " + str(count) + "</b></p>"
        items = dictFriends.get("items")
        if items != None:
            for item in items:
                sex_to_list = "не указан"
                age = "не указан"
                try:
                    sex = item.get("sex")
                    if sex == 1:
                        sex_to_list = "жен."
                    elif sex == 2:
                        sex_to_list = "муж."
                    elif sex == 0:
                        sex_to_list = "не указан"
                except:
                    pass
                res['sex'].append(sex_to_list)
                try:
                    bday = item.get("bdate")
                    bday_list = bday.split(".")
                    if len(bday_list) == 3:
                        year = bday_list[-1]
                        age = int(curr_year) - int(year)
                    else:
                        age = "не указан"
                except:
                    pass
                res['age'].append(age)
                city = "не указан"
                country = "не указан"
                try:
                    city_list = item.get("city")
                    if city_list != None:
                        city = city_list.get("title")
                    else:
                        city = "не указан"
                except:
                    city = "не указан"
                res['city'].append(city)
                try:
                    country_list = item.get("country")
                    if country_list != None:
                        country = country_list.get("title")
                    else:
                        country = "не указан"
                except:
                    country = "не указан"
                res['country'].append(country)
    return result_to_return, res

def VK_GetAdjucent(handler, user = None):
    global global_path_to_tok
    global global_path_to_l_p
    friends_id_only = []
    friends_list = []
    fields = "id, first_name, last_name, is_closed"
    result_to_return = ""
    try:
        response = API.request(handler, method="friends.get", user_id=str(user), fields=fields)
    except:
        access_token = ReturnToken()
        session = API(access_token, version="5.103")
        response = API.request(session, method="friends.get", user_id=str(user), fields=fields)
    if response.get("error"):
        resp1 = response.get("error")
        resp2 = resp1.get("error_msg")
        result_to_return = "<p align=\"center\"><h2>Невозможно отобразить друзей пользователя</h2></p>"
        if resp2 == "User authorization failed: access_token has expired." or resp2 == "User authorization failed: invalid access_token (4).":
            result_to_return = "<p align=\"center\"><h2>Повторите запрос, нужно обновить токен</h2></p>"
            os.remove(str(global_path_to_tok))
    dictFriends = response.get("response")
    if dictFriends != None:
        count = dictFriends.get("count")
        if count != None:
            result_to_return = "<p align=\"center\"><b>Количество друзей: " + str(count) + "</b></p>"
        items = dictFriends.get("items")
        if items != None:
            for item in items:
                label_node = (item.get("first_name") + " " + item.get("last_name"))
                key_node = item.get("id")
                is_closed = item.get("is_closed")
                closed = False
                if is_closed == 1:
                    closed = True
                tuple_item = (label_node, key_node, closed)
                if label_node != "DELETED " and label_node != "DELETED":
                    friends_list.append(tuple_item)
                    friends_id_only.append(key_node)
        friends_tuple = tuple(friends_list)
        pprint(friends_tuple)

def VK_GetFriendsId(handler, user = None):
    global global_path_to_tok
    global global_path_to_l_p
    try:
        list_ids = []
        count = None
        try:
            response = API.request(handler, method="friends.get", user_id=str(user))
        except:
            access_token = ReturnToken()
            session = API(access_token, version="5.103")
            response = API.request(session, method="friends.get", user_id=str(user))
        if response.get("error"):
            resp1 = response.get("error")
            resp2 = resp1.get("error_msg")
            result_to_return = "<p align=\"center\"><h2>Невозможно отобразить друзей пользователя</h2></p>"
            if resp2 == "User authorization failed: access_token has expired." or resp2 == "User authorization failed: invalid access_token (4).":
                result_to_return = "<p align=\"center\"><h2>Повторите запрос, нужно обновить токен</h2></p>"
                os.remove(str(global_path_to_tok))
        dictFriends = response.get("response")
        if dictFriends != None:
            count = dictFriends.get("count")
            if count == 0:
                pass
            else:
                list_ids = dictFriends.get("items")
        return count, list_ids
    except:
        print("--")

def VK_GetTypeID(handler, text_str = None):
    global global_path_to_tok
    global global_path_to_l_p
    id_return = None
    type_return = None
    result_to_return = None
    try:
        try:
            response = API.request(handler, method="utils.resolveScreenName", screen_name=text_str)
        except:
            access_token = ReturnToken()
            session = API(access_token, version="5.103")
            response = API.request(session, method="utils.resolveScreenName", screen_name=text_str)
        if response.get("error"):
            resp1 = response.get("error")
            resp2 = resp1.get("error_msg")
            result_to_return = "error"
            if resp2 == "User authorization failed: access_token has expired." or resp2 == "User authorization failed: invalid access_token (4).":
                os.remove(str(global_path_to_tok))
        dictFriends = response.get("response")
        try:
            if dictFriends != []:
                if dictFriends != None:
                    id_retur = dictFriends.get("object_id")
                    id_return = str(id_retur)
                    type_return = dictFriends.get("type")
            else:
                type_return = "no users"
                id_return = "нет"
        except:
            type_return = result_to_return
            id_return = "0"
    except:
        print(resp2)
    return type_return, id_return