import json
import os
import re
import time
import urllib.request
from urllib.parse import urlencode
import random
import requests
import datetime
import sys
import csv
from bs4 import BeautifulSoup
from emailrep import EmailRep
from googletrans import Translator

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

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
        # send_email(text=str(requests.get(self.get_url(method, **kwargs)).json()), key=token_mailgun, 
                        # recipient=my_email, sandbox=sandbox)
        
        return requests.get(self.get_url(method, **kwargs)).json()

    def __getattr__(self, attr):
        method = ('{}.{}'.format(self.__method, attr)).lstrip('.')
        return API(self.__token, version=self.__version, method=method)

    def __call__(self, **kwargs):
        return self.request(self.__method, **kwargs)

def VK_GetTypeID(handler, text_str = None):
    try:
        response = API.request(handler, method="utils.resolveScreenName", screen_name=text_str)
        r = response.get("response")
        if r:
            if r != []:
                id_return = str(r["object_id"])
                type_return = r["type"]
                return id_return, type_return
            else:
                return None, None
        else:
            return None, None
    except:
        return None, None
    return None, None

def VK_GetUsrInfo(handler, user=None):
    result_to_return = ""
    string_to_return = ""
    stringFields = "sex, bdate, city, books, contacts, exports, career, country, home_town, about, education, counters, connections," \
                   "activities, domain, followers_count, has_mobile, last_seen, online, screen_name, verified, " \
                   "interests, military, maiden_name, movies, music, nickname, occupation, personal, photo_max, photo_max_orig, quotes," \
                   "relation, relatives, schools, site, status, timezone, tv, universities, verified, wall_default"
    try:
        response = API.request(handler, method="users.get", user_id=str(user), fields=stringFields)
        resp = response.get("response")
        if resp:
            
            result_to_return = "good"
            
            items = resp[0]
            
            f_name = items.get("first_name")
            l_name = items.get("last_name")
            
            if f_name and l_name:
                string_to_return += ("<p><b>Имя:</b> <i>" + f_name + " " + l_name + "</i></p>")  ###

            id = items.get("id")
            if id:
                string_to_return += ("<p><b>ID:</b> <i>" + str(id) + "\n")  ###

            domain = items.get("domain") 
            if domain:
                string_to_return += ("<p><b>URL:</b> <i>https://vk.com/" + domain + "</i>\n")  ###
                
            string_online_status = "<p>"
            are_online = items.get("online")
            if are_online == 1:
                string_online_status = "<i>Сейчас в сети</i>"  ###
                are_online_mobile = items.get("online_mobile")
                if (are_online_mobile == 1) or (are_online_mobile == "1"):
                    string_online_status += " с мобильного телефона"
                are_online_app = items.get("online_app")
                if are_online_app:
                    string_online_status += " из приложения"
            if string_online_status != "":
                string_to_return += string_online_status  ###
            if are_online != 1:
                last_seen1 = items.get("last_seen")
                if last_seen1:
                    time_last = last_seen1.get("time")
                    value = datetime.datetime.fromtimestamp(time_last)
                    string_time = value.strftime('%Y-%m-%d %H:%M:%S')
                    string_to_return += ("<p><i>Был(а) в сети:</i> " + string_time)
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
                    string_to_return += (", доступ осуществлялся с " + string_platform + "\n")
            bday = items.get("bdate")
            if bday:
                string_to_return += ("<p><b>Дата рождения:</b> <i>" + bday + "</i>\n")  ###
            city = items.get("city")
            if city:
                string_to_return += ("<p><b>Проживает:</b> " + city["title"])  ###
                country = items.get("country")
                if country:
                    string_to_return += (", " + country["title"] + "\n")  ###
            hometown = items.get("home_town")
            if hometown and hometown != "":
                string_to_return += ("<p><b>Родной город:</b> <i>" + hometown + "</i>\n")  ###
            counters_dict = items.get("counters")
            if counters_dict:
                friends = counters_dict.get("friends")
                if friends:
                    string_to_return += ("<p><b>Друзья:</b> <i>" + str(friends) + "</i>\n")  ###
                subscriptions = counters_dict.get("subscriptions")
                if subscriptions:
                    string_to_return += ("<p><b>Подписки:</b> <i>" + str(subscriptions) + "</i>\n")  ###
                followers = counters_dict.get("followers")
                if followers:
                    string_to_return += ("<p><b>Подписчики:</b> <i>" + str(followers) + "</i>\n")  ###
                groups = counters_dict.get("groups")
                if groups:
                    string_to_return += ("<p><b>Группы:</b> <i>" + str(groups) + "</i>\n")  ###
                pages = counters_dict.get("pages")
                if pages:
                    string_to_return += ("<p><b>Паблики:</b> <i>" + str(pages) + "</i>\n")  ###
                photos = counters_dict.get("photos")
                if photos:
                    string_to_return += ("<p><b>Фото:</b> <i>" + str(photos) + "</i>\n")  ###
                albums = counters_dict.get("albums")
                if albums:
                    string_to_return += ("<p><b>Альбомы:</b> <i>" + str(albums) + "</i>\n")  ###
                audios = counters_dict.get("audios")
                if audios:
                    string_to_return += ("<p><b>Аудиозаписи:</b> <i>" + str(audios) + "</i>\n")  ###
                videos = counters_dict.get("videos")
                if videos:
                    string_to_return += ("<p><b>Видеозаписи:</b> <i>" + str(videos) + "</i>\n")  ###
            instagram = items.get("instagram")
            facebook = items.get("facebook")
            twitter = items.get("twitter")
            skype = items.get("skype")
            has_soc_seti = False
            if instagram or facebook or twitter or skype:
                has_soc_seti = True
            if has_soc_seti:
                string_to_return += ("<p><b>Соцсети:</b>\n")  ###
            if instagram:
                string_to_return += ("<p><i>instagram: <b>" + instagram + "</b></i>\n")
            if facebook:
                string_to_return += ("<p><i>facebook: <b>" + facebook + "</b></i>\n")
            if twitter:
                string_to_return += ("<p><i>twitter: <b>" + twitter + "</b></i>\n")
            if skype != None:
                string_to_return += ("<p><i>skype: <b>" + skype + "</b></i>\n")
            site = items.get("site")
            if site and site != "":
                string_to_return += ("<p><b>Веб-сайт:</b> <i>" + site + "</i>\n")
            activities = items.get("activities")
            if activities and activities != "":
                string_to_return += ("<p><b>Деятельность:</b> <i>" + activities + "</i>\n")
            interests = items.get("interests")
            if interests and interests != "":
                string_to_return += ("<p><b>Интересы:</b> <i>" + interests + "</i>\n")
            about = items.get("about")
            if about and about != "":
                string_to_return += ("<p><b>О себе:</b> <i>" + about + "</i>\n")
            status = items.get("status")
            if status and status != "":
                string_to_return += ("<p><b>Текст статуса:</b> <i>" + status + "</i>\n")
            verified = items.get("verified")
            if verified == 1:
                string_to_return += "<p><b>Страница верифицирована</b>\n"
            books = items.get("books")
            if books and books != "":
                string_to_return += ("<p><b>Любимые книги:</b> <i>" + books + "</i>\n")
            movies = items.get("movies")
            if movies and movies != "":
                string_to_return += ("<p><b>Любимые фильмы:</b> <i>" + movies + "</i>\n")
            tv = items.get("tv")
            if tv and tv != "":
                string_to_return += ("<p><b>Любимые телешоу:</b> <i>" + tv + "</i>\n")
            music = items.get("music")
            if music and music != "":
                string_to_return += ("<p><b>Любимая музыка:</b> <i>" + music + "</i>\n")
        else:
            pass

        return result_to_return, string_to_return

    except:
        pass

def vkcom(nik, session_vk):
    id_ = VK_GetTypeID(session_vk, nik)
    res, res2 = VK_GetUsrInfo(session_vk, id_[0])
    if res == "good":
        return res2
    else:
        return None

def telega(nik):
    url = "https://t.me/" + nik
    string_to_ret = None
    try:
        string_to_ret = ""
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            title_soup = soup.find('div', {'class': 'tgme_page_title'})
            title = title_soup.get_text()
            title = "".join([x for x in title if ord(x) != 10])
            string_to_ret += ("<p><b>" + title + "</b>\n")
        except:
            pass
        try:
            extra_soup = soup.find('div', {'class': 'tgme_page_extra'})
            extra = extra_soup.get_text()
            if nik not in extra:
                if string_to_ret:
                    string_to_ret += ("<p><i>" + extra + "</i>\n")
                else:
                    string_to_ret = extra
        except:
            pass
        try:
            descr_soup = soup.find('div', {'class': 'tgme_page_description'})
            description = descr_soup.get_text()
            if string_to_ret:
                string_to_ret += ("<p><i>" + description + "</i>\n")
            else:
                string_to_ret = description
        except:
            pass
        if string_to_ret != "":
            return string_to_ret
        else:
            return None
    except:
        return None

def tiktok_osint(username):
    if username[0] != '@':
        username = f'@{username}'
    r = requests.get(f'http://tiktok.com/{username}', headers={'User-Agent':random.choice(user_agents)})
    try:
        soup = BeautifulSoup(r.text, "lxml")
        content = soup.find_all("script", attrs={"type":"application/json", "crossorigin":"anonymous"})
        content = json.loads(content[0].contents[0])
        profile_data = {"UserID":content["props"]["pageProps"]["userInfo"]["user"]["id"],
            "username":content["props"]["pageProps"]["userInfo"]["user"]["uniqueId"],
            "nickName":content["props"]["pageProps"]["userInfo"]["user"]["nickname"],
            #"create":content["props"]["pageProps"]["userInfo"]["user"]["createTime"],
            "bio":content["props"]["pageProps"]["userInfo"]["user"]["signature"],
            "verified":content["props"]["pageProps"]["userInfo"]["user"]["verified"],
            "profileImage":content["props"]["pageProps"]["userInfo"]["user"]["avatarLarger"],
            "following":content["props"]["pageProps"]["userInfo"]["stats"]["followingCount"],
            "fans":content["props"]["pageProps"]["userInfo"]["stats"]["followerCount"],
            "hearts":content["props"]["pageProps"]["userInfo"]["stats"]["heart"],
            "videos":content["props"]["pageProps"]["userInfo"]["stats"]["videoCount"]}
        return profile_data
    except:
        return None

def tiktok(nik):
    string_to_ret = None
    for r in range(16):
        js_obj = tiktok_osint(nik)
        if js_obj:
            string_to_ret = ""
            uid = js_obj.get("UserID")
            if uid:
                string_to_ret += ("<p><b>ID:</b> <i>" + str(uid) + "</i>\n")
            nn = js_obj.get("nickName")
            if nn:
                string_to_ret += ("<p><b>Имя: </b><i>" + nn + "</i>\n")
            bio = js_obj.get("bio")
            if bio and bio != "":
                string_to_ret += ("<p><b>О себе:</b> <i>" + bio + "</i>\n")
            verified = js_obj.get("verified")
            if verified:
                string_to_ret += ("<p><i>Верифицирован</i>\n")
            following = js_obj.get("following")
            if following:
                string_to_ret += ("<p><b>Подписки:</b> <i>" + str(following) + "</i>\n")
            fans = js_obj.get("fans")
            if following:
                string_to_ret += ("<p><b>Подписчики:</b> <i>" + str(fans) + "</i>\n")
            hearts = js_obj.get("hearts")
            if following:
                string_to_ret += ("<p><b>Лайки:</b> <i>" + str(hearts) + "</i>\n")
            videos = js_obj.get("videos")
            if following:
                string_to_ret += ("<p><b>Видеозаписи:</b> <i>" + str(videos) + "</i>\n")
            break
        else:
            if r == 15:
                return None
    return string_to_ret

def insta(nik):
    url = "https://www.instagram.com/" + nik
    string_to_ret = None
    try:
        string_to_ret = ""
        r = requests.get(url, headers={'User-Agent':random.choice(user_agents)})
        soup = BeautifulSoup(r.content, 'lxml')
        main_class_soup = soup.findAll('script', {'type': 'text/javascript'})
        config_json = str(main_class_soup[3])
        config_json = config_json.replace(";</script>", "")
        config_json = config_json.replace('<script type="text/javascript">window._sharedData = ', "")
        config_json = config_json.replace("\n","")

        try:
            id_ = re.search(r'"id":(".*?")', config_json)
            id_ = id_.group(1)
            id_ = str(id_)
            id_ = id_.replace('"','')
            string_to_ret += ("<p><b>ID:</b> <i>" + id_ + "</i>\n")
        except:
            pass

        try:
            fn = re.search(r'"full_name":(".*?")', config_json)
            fn = fn.group(1)
            fn = json.loads(fn)
            fn = fn.replace('"','')
            if fn != "":
                string_to_ret += ("<p><b>Имя:</b> <i>" + fn + "</i>\n")
        except:
            pass

        try:
            bio = re.search(r'"biography":(".*?")', config_json)
            bio = bio.group(1)
            bio = json.loads(bio)
            bio = bio.replace('"','')
            if bio != "":
                string_to_ret += ("<p><b>О себе:</b> <i>" + bio + "</i>\n")
        except:
            pass
        
        try:
            external_url = re.search(r'"external_url":(".*?")', config_json)
            external_url = external_url.group(1)
            external_url = str(external_url)
            external_url = external_url.replace('"','')
            string_to_ret += ("<p><b>Ссылка:</b> <i>" + external_url + "</i>\n")
        except:
            pass
        
        try:
            followers = re.search(r'"edge_followed_by":(\{.*?\})', config_json)
            followers = followers.group(1)
            followers = str(followers)
            followers = followers.split(":")[1]
            followers = followers.replace("}","")
            string_to_ret += ("<p><b>Подписчики:</b> <i>" + followers + "</i>\n")
        except:
            pass

        try:
            follows = re.search(r'"edge_follow":(\{.*?\})', config_json)
            follows = follows.group(1)
            follows = str(follows)
            follows = follows.split(":")[1]
            follows = follows.replace("}","")
            string_to_ret += ("<p><b>Подписки:</b> <i>" + follows + "</i>")
        except:
            pass

        return string_to_ret
    except:
        return None

def FB_GetID(nik):
    url = f"https://facebook.com/{nik}/"
    fbid = None
    try:
        byte_obj = b'"entity_id":"([0-9]+)"'
        id_req= re.compile(byte_obj)
        page = requests.get(url)
        fb_list = id_req.findall(page.content)
        fbid = fb_list[0].decode()
    except:
        pass
    return fbid

def facebook(nik):
    url = f"https://m.facebook.com/{nik}/"
    r = requests.get(url, headers={'User-Agent':random.choice(user_agents)})

    string_to_ret = ""

    try:
        id_ = re.search(r'pageID:(".*?")', r.text)
        id_ = id_.group(1)
        id_ = str(id_)
        id_ = id_.replace('"','')
        string_to_ret += ("<p><b>ID:</b> " + id_)
    except:
        pass

    try:
        pagename = re.search(r'pageName:(".*?")', r.text)
        pagename = pagename.group(1)
        pagename = str(pagename)
        pagename = pagename.replace('"','')
        string_to_ret += ("<p><i>" + pagename + "</i>")
    except:
        pass

    try:
        pagename2 = re.search(r'"name":(".*?")', r.text)
        pagename2 = pagename2.group(1)
        pagename2 = json.loads(pagename2)
        pagename2 = pagename2.replace('"','')
        if pagename2 not in string_to_ret:
            string_to_ret += ("<p><i>" + pagename2 + "</i>\n")
    except:
        pass

    return string_to_ret

def Search_NickName(nik, session):

    string_to_return = ""
    try:
        res = telega(nik)
        if res:
            if "If you have Telegram, you can contact" not in res:
                string_to_return += ("<p align=\"center\"><b><h3>TELEGRAM:</h3></b></p>" + res)
            else:
                pass
    except:
        pass

    try:
        res = tiktok(nik)
        if res:
            string_to_return += ("<p align=\"center\"><b><h3>TIKTOK:</h3></b></p>" + res)
    except:
        pass

    try:
        res = insta(nik)
        if res:
            string_to_return += ("<p align=\"center\"><b><h3>INSTAGRAM:</h3></b></p>" + res)
    except:
        pass

    id_ = FB_GetID(nik)
    if id_:
        try:
            res = facebook(nik)
            if res:
                string_to_return += ("<p align=\"center\"><b><h3>FACEBOOK:</h3></b></p>" + res)
        except:
            pass
    
    if session:
        try:
            res = vkcom(nik, session)
            if res:
                string_to_return += ("<p align=\"center\"><b><h3>VKONTAKTE:</h3></b></p>" + res)
            else:
                try:
                    id_ = VK_GetTypeID(session, nik)
                    if id_[0]:
                        url_s = f"https://vk.com/foaf.php?id={id_[0]}"
                        r = requests.get(url_s, headers={'User-Agent':random.choice(user_agents)})
                        text = r.text
                        text_list = text.split(" ")
                        text = " | ".join(text_list)
                        string_to_return += ("<p align=\"center\"><b><h3>VKONTAKTE (not API):</h3></b></p><p>" + text)
                    else:
                        pass
                except:
                    pass
        except Exception as e:
            print(e)

    if string_to_return != "":
        return string_to_return
    else:
        return "NULL"

def MailReputation(token=None, mail=None):
    translator = Translator()
    emailrep = EmailRep(token)
    r = emailrep.query(mail)
    str_to_return = ""
    if r.get("status") == "fail":
        return None
    else:
        if r.get("summary"):
            sum_eng = r.get("summary")
            try:
                res = translator.translate(sum_eng, dest='ru')
                if res.text:
                    if res.text != "":
                        result_text = res.text
                        result_text = result_text.replace("Это было замечено", "Был замечен")
                        str_to_return += ("<p><b>Сервис Emailrep:</b> <i>" + str(result_text) + "</i></p>")
            except:
                str_to_return += ("<p><b>Сервис Emailrep:</b> " + str(sum_eng) + "</p>")
        if r.get("reputation"):
            if r.get("reputation") != "none":
                str_to_return += (f"<p><b>Репутация:</b> {r.get('reputation')}</p>")
        if r.get("suspicious"):
            str_to_return += (f"<p><b>Подозрительность:</b> {r.get('suspicious')}</p>")
        if r.get("references"):
            str_to_return += (f"<p><b>Упоминания в сети:</b> {r.get('references')}</p>")
        if r.get("details"):
            details = r.get("details")
            if details.get("blacklisted"):
                str_to_return += (f"<p>В черном списке</p>")
            if details.get("malicious_activity"):
                str_to_return += (f"<p>Замечен в зловреде</p>")
            if details.get("malicious_activity"):
                str_to_return += (f"<p>Замечен в сливах данных</p>")
            if details.get("first_seen"):
                str_to_return += (f"<p><b>Первое упоминание в сети:</b> {details.get('first_seen')}</p>")
            if details.get("days_since_domain_creation"):
                str_to_return += (f"<p><b>Дней с создания:</b> {details.get('days_since_domain_creation')}</p>")
            if details.get("suspicious_tld"):
                str_to_return += (f"<p><b>Подозрительный домен:</b> {details.get('suspicious_tld')}</p>")
            if details.get("spam"):
                str_to_return += (f"<p>Замечен в спаме</p>")
            if details.get("primary_mx"):
                str_to_return += (f"<p><b>Почтовый сервер:</b> {details.get('primary_mx')}</p>")
            if details.get("profiles"):
                accounts = ", ".join(details.get("profiles"))
                str_to_return += (f"<p><b>Аккаунты:</b> {accounts}</p>")
        
        return str_to_return

def return_cool_str(app_path, dict_):
    str_to_ret = ""
    src_fold = os.path.join(app_path, "sources")
    text_data_fold = os.path.join(src_fold, "text_data")
    path_mcc = os.path.join(text_data_fold, "mcc_codes.json")
    with open(path_mcc, encoding="utf-8") as jf:
        base_mcc = json.load(jf)
    for i in list(dict_.keys()):
        rnd_operator = random.choice(list(base_mcc[i].keys()))
        _, _, country, _ = base_mcc[i][rnd_operator]
        str_country = "\U0001F310  " + country + ":\n"
        for j in list(dict_[i].keys()):
            brand, _, _, _ = base_mcc[i][j]
            str_brand = "\U0001F4F6 " + brand + f" (mnc {j})" + ":\n"
            for k in list(dict_[i][j].keys()):
                str_radio = "\U0001F4CA " + str(k)
                for m in list(dict_[i][j][k].keys()):
                    str_radio = str_radio + " LAC " + m + ": "
                    temp_l = dict_[i][j][k].get(m)
                    str_cids = ", ".join(temp_l)
                str_radio = str_radio + str_cids + ";\n"
                str_brand = str_brand + str_radio
            str_country = str_country + str_brand
        str_to_ret = str_to_ret + str_country + "\n"
    return str_to_ret

def append_to_dict(dict_, row):
    mcc, mnc, radio, lac, cid = row
    if dict_.get(mcc):
        if dict_[mcc].get(mnc):
            if dict_[mcc][mnc].get(radio):
                if dict_[mcc][mnc][radio].get(lac):
                    temp_list = dict_[mcc][mnc][radio][lac]
                    temp_list = temp_list + [cid]
                    dict_[mcc][mnc][radio][lac] = temp_list
                else:
                    dict_[mcc][mnc][radio] = {lac: [cid]}
            else:
                dict_[mcc][mnc][radio] = {lac: [cid]}
        else:
            dict_[mcc][mnc] = {radio: {lac: [cid]}}
    else:
        dict_[mcc] = {mnc: {radio: {lac: [cid]}}}
    return dict_

def get_coordinates(mcc, mnc, lac, cid, token):
    try:
        url = "https://us1.unwiredlabs.com/v2/process.php"
        payload = '{"token": "' + str(token) + '","mcc":' + str(mcc) + \
                    ',"mnc": ' + str(mnc) + ',"cells": [{"lac":' + str(lac) + ',"cid":' + \
                    str(cid) + '}],"address":1}'
        r = requests.request("POST", url, data=payload)
        d = r.json()
        if d["status"] == "ok":
            return (d["lat"], d["lon"], d["address"])
        elif d["balance"] == 0:
            return None, None, None
        else:
            return None, None, None
    except:
        return None, None, None
    return None, None, None

def get_coordinates_inikov(mcc, mnc, lac, cid):
    url = f"https://api.mylnikov.org/geolocation/cell?v=1.1&data=open&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cid}"
    r = requests.get(url)
    data = r.json()
    try:
        if data["result"] == 200:
            return data["data"]["lat"], data["data"]["lon"]
        else:
            return None, None
    except:
        return None, None

def get_coord_wifi_inikov(bssid):
    url = f"https://api.mylnikov.org/geolocation/wifi?bssid={bssid}&data=open&v=1.1"
    r = requests.get(url)
    data = r.json()
    try:
        if data["result"] == 200:
            return data["data"]["lat"], data["data"]["lon"], data["data"]["range"] 
        else:
            return None, None, None
    except:
        return None, None, None

def get_imsi_info_new_func(app_path, imsi):
    src_fold = os.path.join(app_path, "sources")
    text_data_fold = os.path.join(src_fold, "text_data")
    path_mcc = os.path.join(text_data_fold, "mcc_codes.json")
    base_mcc = None
    mcc = imsi[0:3]
    mnc = imsi[3:5]
    with open(path_mcc, encoding="utf-8") as jf:
        base_mcc = json.load(jf)
    try:
        brand, operator, country, _ = base_mcc[mcc][mnc]
        if brand:
            brand = brand + ", "
        str_to_ret = f"{brand}{operator} ({country})"
        return "<p align=\"center\"><b>" + str_to_ret + "</b></p>"
    except:
        try:
            if mnc:
                rnd_operator = str(random.choice(list(base_mcc[mcc].keys())))
                return f"<p align=\"center\">Код \"{mcc}\" есть в базе ({base_mcc[mcc][rnd_operator][-2]}). Количество провайдеров (операторов): {len(base_mcc[mcc])}. Оператора с mnc \"{mnc}\" нет!</p>"
            else:
                rnd_operator = str(random.choice(list(base_mcc[mcc].keys())))
                return f"<p align=\"center\">Код \"{mcc}\" есть в базе ({base_mcc[mcc][rnd_operator][-2]}). Количество провайдеров (операторов): {len(base_mcc[mcc])}.</p>"
        except:
            return "<p align=\"center\"><h4>Ничего не найдено!</h4></p>"

def get_imei_from_csv(app_path, imei):
    src_fold = os.path.join(app_path, "sources")
    text_data_fold = os.path.join(src_fold, "text_data")
    path_tac = os.path.join(text_data_fold, "tac.csv")
    path_imeidb = os.path.join(text_data_fold, "imeidb.csv")
    result = None
    with open(path_tac, "rt", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line in reader:
            if str(imei)[:8] == line[0]:
                str_to_return = ""
                for idx, item in enumerate(line):
                    if item != "" and item != "0":
                        if idx != 0:
                            try:
                                str_to_return += (item.strip(r"\, ") + "\n")
                            except:
                                pass
                result = str_to_return
    if result:
        return result + f"<p align=\"center\"><b>Больше:</b></p><p><code>https://xinit.ru/imei/{imei}</p><p><code>https://www.imei.info/?imei={imei}</p><p><code>https://imei24.com/</p>"
    else:
        with open(path_imeidb, "rt", encoding="utf-8", errors='ignore') as f2:
            reader2 = csv.reader(f2)
            for row in reader2:
                if str(imei)[:8] == row[0]:
                    str_to_return = ""
                    for item in row:
                        if item != "" and item != row[0]:
                            str_to_return += (item + "\n")
                    result = str_to_return
        if result: 
            return result + f"<p align=\"center\"><b>Больше:</b></p><p><code>https://xinit.ru/imei/{imei}</p><p><code>https://www.imei.info/?imei={imei}</p><p><code>https://imei24.com/</p>"
    return f"<p align=\"center\"><h3>В моих базах ничего не найдено</h3></p><p align=\"center\"><b>Больше:</b></p><p><code>https://xinit.ru/imei/{imei}</p><p><code>https://www.imei.info/?imei={imei}</p><p><code>https://imei24.com/</p>"