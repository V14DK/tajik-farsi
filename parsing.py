import math
import requests
import multiprocessing
import pandas as pd
from bs4 import BeautifulSoup
from parsivar import Tokenizer
from parsivar import Normalizer
from finding import Finder


class Parser:
    def __init__(self, urls):
        self.urls = pd.read_csv(urls)
        self.soup = BeautifulSoup
        self.normalizer = Normalizer()
        self.tokenizer = Tokenizer()

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
            quotes = soup.find_all('main') if soup.find_all('main') \
                else soup.find_all('div', class_='bodytext')
        result = ''
        for quote in quotes:
            result += quote.text
        return result

    def __parse_text_to_sentences(self, url):
        sentences = {'tajik': self.__parse_html_to_text(url[0]),
                     'farsi': self.__parse_html_to_text(url[1])}
        sentences['tajik'] = [s+'.' for s in sentences['tajik'].rstrip().lstrip().split('.') if s]
        sentences['farsi'] = [s for s in self.tokenizer.tokenize_sentences(
            self.normalizer.normalize(sentences['farsi'])) if s]
        return sentences

    def parse_corpus(self, start, final, result):
        for i in range(start, final):
            sentences = self.__parse_text_to_sentences(self.urls.iloc[i])
            pairs = Finder.find_pairs(sentences)
            result[i] = pairs

    def get_sentences(self):
        len_urls = self.urls.shape[0]
        manager = multiprocessing.Manager()
        n_proc = multiprocessing.cpu_count()
        result = manager.dict({i: manager.list([]) for i in range(len_urls)})
        processes = [0 for _ in range(n_proc)]
        start = 0
        for i in range(n_proc):
            ceil = math.ceil(len_urls / n_proc) * (i + 1)
            final = ceil if ceil < len_urls else len_urls
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
        pairs = {'tajik': [], 'farsi': []}
        for i in range(len(result)):
            pairs['tajik'] += result[i]['tajik']
            pairs['farsi'] += result[i]['farsi']
        pairs = pd.DataFrame(pairs)
        pairs.to_csv('pairs.csv', index_label='id')
