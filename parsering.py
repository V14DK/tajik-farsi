import math
import requests
import multiprocessing
import pandas as pd
from finding import Finder
from bs4 import BeautifulSoup
from parsivar import Tokenizer
from parsivar import Normalizer


class Parser:
    def __init__(self, urls):
        self.urls = pd.read_csv(urls)
        self.soup = BeautifulSoup

    @staticmethod
    def __delete_tags(soup):
        figure = soup.figure
        section = soup.section
        h1 = soup.h1
        t = soup.time
        while figure:
            figure.decompose()
            figure = soup.figure
        while section:
            section.decompose()
            section = soup.section
        while h1:
            h1.decompose()
            h1 = soup.h1
        while t:
            t.decompose()
            t = soup.time

    def __parse_html_to_text(self, url):
        response = requests.get(url)
        soup = self.soup(response.text, 'lxml')
        self.__delete_tags(soup)
        if 'tajik' in url:
            quotes = soup.find_all('div', class_='story-body__inner')
        else:
            quotes = soup.find_all('main') if soup.find_all('main') else soup.find_all('div', class_='bodytext')
        result = ''
        for quote in quotes:
            result += quote.text
        return result

    def __parse_text_to_sentences(self, url):
        sentences = {'tajik': self.__parse_html_to_text(url[0]), 'farsi': self.__parse_html_to_text(url[1])}
        my_normalizer = Normalizer()
        my_tokenizer = Tokenizer()
        sentences['tajik'] = [s+'.' for s in sentences['tajik'].rstrip().lstrip().split('.') if s]
        sentences['farsi'] = [s for s in my_tokenizer.tokenize_sentences(my_normalizer.normalize(sentences['farsi'])) if s]
        return sentences

    def parse_corpus(self, start, final, result):
        #для тестирования брал только первый блок
        # for i in range(start, final):
            sentences = self.__parse_text_to_sentences(self.urls.iloc[0])
            pairs = Finder.find_pairs(sentences)
            # if i < self.urls.shape[0]:
            result[0] = pairs

    def get_sentences(self):
        #создается столько ячеек в result, сколько пар текстов имеется,
        #чтобы можно было сразу после получения параллельных текстов вытащить из них
        #параллельные предложения.
        #возможна проблема с api, когда будет поступать много запросов на перевод,
        #т.к. одновременно будет запущено (количество ядер) процессов, плюс, возможно, стоит
        #использовать asyncio, т.к. тут уже более I/O-bound операции, чем раньше, что,
        #скорее всего, нивелирует преимущества работы на нескольких процессах
        manager = multiprocessing.Manager()
        n_proc = multiprocessing.cpu_count()
        result = manager.dict({i: manager.list([]) for i in range(self.url.shape[0])})
        processes = [0 for _ in range(n_proc)]
        start = 0
        for i in range(n_proc):
            final = math.ceil(self.urls.shape[0] / n_proc) * (i + 1)
            processes[i] = multiprocessing.Process(target=self.parse_corpus,
                                                   args=(start, final, result))
            start = final
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        return result

    @staticmethod
    def sentences_to_csv(result):
        #начал переделывать для параллельных предложений
        pairs = [[result[i][0], result[i][1]] for i in range(len(result))]
        result_t = []
        result_f = []
        tajik = pd.DataFrame({'tajik': list(result_t)})
        farsi = pd.DataFrame({'farsi': list(result_f)})
        tajik.to_csv('tajik.csv', index_label='id')
        farsi.to_csv('farsi.csv', index_label='id')
        tajik = pd.read_csv('tajik.csv')
        farsi = pd.read_csv('farsi.csv')
        result = tajik.merge(farsi, how='outer')
        result.to_csv('result.csv', index=False)
