# SOVA App
![](https://github.com/uav-profile/SOVA-App/blob/main/sources/images/about.jpg)

Данное ПО создано в образовательных целях - изучение возможностей получения информации из сети <a href="https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82">"Интернет"</a>.
<br><br><b>Состав и назначение основных элементов:</b>
<br>Вкладка <code><b>"REST API"</b></code>
<br> Реализовано получение информации от различных API-сервисов:
<br> * <a href="https://github.com/uav-profile/SOVA-App/blob/main/sources/text_data/mcc_codes.json">об операторе/регионе по IMSI-идентификатору</a>;
<br> * <a href="https://htmlweb.ru">о российском/международном абонентском номере</a>;
<br> * <a href="https://ipinfo.io/signup">об IP-адресе</a>;
<br> * <a href="https://www.opencellid.org">о месте по координатам, получение координат объекта</a>;
<br> * <a href="https://www.opencellid.org">о близлежащих базовых станциях GSM,UMTS,LTE вокруг указанной точки (сохранение отчета со списком станций, возможно вывести на карте)</a>.
<br> С помощью движка <a href="https://github.com/snooppr/snoop"> [snoop project] </a> имеется возможность просмотреть никнейм пользователя в базе 1027 сайтов.
<br>
<br> Вкладки <code><b>"<a href="https://vk.com/">vk.com</a>","<a href="https://www.instagram.com/accounts/emailsignup/?hl=ru">instagram.com</a>"</b></code> содержат поля для ввода ключевой информации и область для просмотра результатов. Имеется функция сохранения результатов в html-файл.
<br>
<br> Возникают ситуации, когда результаты имеют ссылки на графические объекты или найденный пользователь представляет интерес и нужно найти больше информации вручную - в правой части программы имеются модули для просмотра картинок. Также имеется поле для записей - "Черновик". Реализована возможность изменения цветового оформления и включение звуковых уведомлений.


![](https://github.com/uav-profile/SOVA-App/blob/main/sources/to_git/1.PNG)


### Запуск можно осуществить 3 способами (выбрать <i>один</i> из трех вариантов):

### 1. <a href="https://github.com/uav-profile/SOVA-App/releases/download/v0.0.2/SOVA.Setup.exe">Скачать и установить setup-версию (win10-x64) (~88.7 Мб)</a> ![](https://github.com/uav-profile/SOVA-App/blob/main/sources/to_git/Down.png), <i>записать логины/пароли/токены</i> в текстовые файлы в каталоге <b>tokens</b> (см. подробнее во вкладке "Помощь"). Запустить <i>SOVA.exe</i>.

### 2. <a href="https://github.com/uav-profile/SOVA-App/releases/download/v0.0.2-zip/SOVA-archieve-win-amd64-3.7.exe">Скачать и распаковать portable-версию (архив) (win10-x64) (~116 Мб)</a> ![](https://github.com/uav-profile/SOVA-App/blob/main/sources/to_git/Down.png), <i>записать логины/пароли/токены</i> в текстовые файлы в каталоге <b>tokens</b> (см. подробнее во вкладке "Помощь"). Запустить <i>SOVA.exe</i>.

### 3. <a href="https://github.com/uav-profile/SOVA-App/archive/main.zip">Скачать исходные файлы</a> ![](https://github.com/uav-profile/SOVA-App/blob/main/sources/to_git/Hourglass.png) . Перед запуском необходимо установить <a href="https://www.python.org/downloads/">python</a> и <a href="https://pypi.org/search/">зависимости</a> (необходимые библиотеки), <i>записать логины/пароли/токены</i> в текстовые файлы в каталоге <b>tokens</b> (см. подробнее во вкладке "Помощь").

### Установка зависимостей с помощью утилиты pip (командная строка):
    pip3 install matplotlib pandas folium pyqt5 requests urllib3==1.24.3 requests-futures requests_toolbelt geopy playsound

### Выполнить (командная строка):
    python \\<путь_к_скрипту>\\SOVA.py 
    python3 \\<путь_к_скрипту>\\SOVA.py
 
    

# ![](https://github.com/uav-profile/SOVA-App/blob/main/sources/to_git/Ok.png) <a href="https://t.me/SovaAppBot"> TELEGRAM BOT</a>: <code>@SovaAppBot</code>    
    
![](https://github.com/uav-profile/SOVA-App/blob/main/sources/to_git/tg.png)      


# Отказ от ответственности:
   Данное Программное Обеспечение (далее - ПО) создано в образовательных целях и не предполагает использование в коммерческих. Устанавливая данное ПО вы соглашаетесь не предпринимать действий, которые могут рассматриваться, как нарушающие российское законодательство или нормы международного права, в том числе в сфере интеллектуальной собственности, авторских и/или смежных правах, а также любых действий, которые приводят или могут привести к нарушению нормальной работы программы. Автор ПО не несет ответственности за результаты и последствия использования данного программного продукта. Любые действия, связанные с возможностями, содержащимися в ПО, являются исключительно вашей ответственностью. Неправомерное использование информации, полученной с помощью данного ПО может привести к уголовному обвинению лиц, о которых идет речь. Автор ПО не будет привлечен к ответственности в случае предъявления любых уголовных обвинений любым лицам, злоупотребляющим полученной информацией.
