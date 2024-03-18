"""
Нагрузка плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from datetime import datetime
# from selenium.webdriver.chrome.webdriver import WebDriver
import requests
from bs4 import BeautifulSoup

from src.spp.types import SPP_document


class ISO:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'iso'
    _content_document: list[SPP_document]

    def __init__(self, last_document: SPP_document, max_count_documents: int = 100, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []

        # self.driver = webdriver
        self.max_count_documents = max_count_documents

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        urls = []
        dates = []
        abstracts = []
        tech_coms = []
        icss = []
        date_begin = datetime(2019, 1, 1)
        #
        #
        # Вернуть назад )
        for URL in [self.URLS[0], ]:
            req = requests.get(URL)
            if req.status_code == 200:
                req.encoding = "UTF-8"
                soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')

                for links in soup.find_all("div", class_="fw-semibold"):
                    if links.find("a").find("i").get("class")[0] != "bi-slash-circle" and \
                            links.find("a").find("i").get("class")[0] != "bi-record-circle":
                        number = ((str(links.find("a").get('href'))).replace("/standard/", "").replace(".html", ""))
                        pattern = f"https://www.iso.org/obp/ui/#!iso:std:{number}:en"
                        date_url = f"https://www.iso.org/standard/{number}.html"
                        date_request = requests.get(date_url)
                        if date_request.status_code == 200:
                            date_soup = BeautifulSoup(date_request.content.decode('utf-8'), 'html.parser')
                            for j in date_soup.find_all("ul", class_="refine"):
                                for k in j.find_all('li'):
                                    for l1 in k.find_all("div", class_="clearfix"):
                                        tech_com = l1.text.replace('\n', ' ').replace('\t', ' ').replace("¶",
                                                                                                         " ").replace(
                                            "▲", " ").replace('\xa0', ' ').replace('\r', ' ').replace('—', "-").replace(
                                            "’",
                                            "'").replace(
                                            "“", '"').replace("”", '"').replace(" ", " ").replace("<", "_").replace(">",
                                                                                                                    "_").replace(
                                            ":", "_").replace('"', "_").replace("/",
                                                                                "_").replace(
                                            "\\", "_").replace("|", "_").replace("?", "_").replace("*", "_")
                                        while "  " in tech_com:
                                            tech_com = tech_com.replace("  ", "")
                                    for l1 in k.find_all("dl", class_="dl-inline no-bottom-margin"):
                                        ics = l1.text.replace('\n', ' ').replace('\t', ' ').replace("¶", " ").replace(
                                            "▲",
                                            " ").replace(
                                            '\xa0', ' ').replace('\r', ' ').replace('—', "-").replace("’", "'").replace(
                                            "“",
                                            '"').replace(
                                            "”", '"').replace(" ", " ").replace("<", "_").replace(">", "_").replace(":",
                                                                                                                    "_").replace(
                                            '"', "_").replace("/",
                                                              "_").replace(
                                            "\\", "_").replace("|", "_").replace("?", "_").replace("*", "_")
                                        while "  " in ics:
                                            ics = ics.replace("  ", "")
                            for j in date_soup.find_all("div", itemprop="description"):
                                abstract = j.get_text().replace('\n', ' ').replace('\t', ' ').replace("¶", " ").replace(
                                    "▲",
                                    " ").replace(
                                    '\xa0', ' ').replace('\r', ' ').replace('—', "-").replace("’", "'").replace("“",
                                                                                                                '"').replace(
                                    "”", '"').replace(" ", " ").replace("<", "_").replace(">", "_").replace(":",
                                                                                                            "_").replace(
                                    '"', "_").replace("/",
                                                      "_").replace(
                                    "\\", "_").replace("|", "_").replace("?", "_").replace("*", "_")
                                while "  " in abstract:
                                    abstract = abstract.replace("  ", "")
                            for j in date_soup.find_all("li"):
                                for k in j.find_all("div", class_="col-sm-6"):
                                    for l1 in k.find_all("div", class_="entry-label"):
                                        if l1.text == "Publication date":
                                            date = k.find("span").text + "-01"
                                            news_date = datetime.strptime(date, '%Y-%m-%d')
                                            if pattern not in urls and news_date > date_begin:
                                                urls.append(pattern)
                                                dates.append(news_date)
                                                abstracts.append(abstract)
                                                tech_coms.append(tech_com)
                                                icss.append(ics)
                                                print("Занесение ссылки:", pattern)

                                                doc = SPP_document(
                                                    None,
                                                    title=date_url,
                                                    abstract=abstract,
                                                    text=None,
                                                    web_link=pattern,
                                                    local_link=None,
                                                    other_data={
                                                        'tech_coms': tech_com,
                                                        'ics': ics
                                                    },
                                                    pub_date=news_date,
                                                    load_date=None,
                                                )

                                                self._content_document.append(doc)

                                                # Логирование найденного документа
                                                self.logger.info(self._find_document_text_for_logger(doc))
                        else:
                            self.logger.error('Ошибка загрузки')
            else:
                self.logger.error('Ошибка загрузки')
                raise requests.exceptions.RequestException('Источник недоступен')


        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    @staticmethod
    def some_necessary_method():
        """
        Если для парсинга нужен какой-то метод, то его нужно писать в классе.

        Например: конвертация дат и времени, конвертация версий документов и т. д.
        :return:
        :rtype:
        """
        ...

    @staticmethod
    def nasty_download(driver, path: str, url: str) -> str:
        """
        Метод для "противных" источников. Для разных источника он может отличаться.
        Но основной его задачей является:
            доведение driver селениума до файла непосредственно.

            Например: пройти куки, ввод форм и т. п.

        Метод скачивает документ по пути, указанному в driver, и возвращает имя файла, который был сохранен
        :param driver: WebInstallDriver, должен быть с настроенным местом скачивания
        :_type driver: WebInstallDriver
        :param url:
        :_type url:
        :return:
        :rtype:
        """

        with driver:
            driver.set_page_load_timeout(40)
            driver.get(url=url)
            time.sleep(1)

            # ========================================
            # Тут должен находится блок кода, отвечающий за конкретный источник
            # -
            # ---
            # ========================================

            # Ожидание полной загрузки файла
            while not os.path.exists(path + '/' + url.split('/')[-1]):
                time.sleep(1)

            if os.path.isfile(path + '/' + url.split('/')[-1]):
                # filename
                return url.split('/')[-1]
            else:
                return ""
