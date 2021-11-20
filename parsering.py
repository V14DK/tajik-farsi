import math
import requests
import multiprocessing
import pandas as pd
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

    def __parse_text_to_sentences(self, url, result, id):
        sentences = self.__parse_html_to_text(url)
        if 'tajik' in url:
            sentences = [s for s in sentences.rstrip().lstrip().split('.') if s]
            result[id] += sentences
        else:
            my_normalizer = Normalizer()
            my_tokenizer = Tokenizer()
            sentences = [s for s in my_tokenizer.tokenize_sentences(my_normalizer.normalize(sentences)) if s]
            result[id] += sentences

    def parse_corpus(self, language, result, id, start, final):
        for i in range(start, final):
            self.__parse_text_to_sentences(self.urls[language + ' url'][i], result, id)

    def get_sentences(self):
        manager = multiprocessing.Manager()
        n_proc = multiprocessing.cpu_count()
        result = manager.dict({i: manager.list([]) for i in range(n_proc)})
        processes = [0 for _ in range(n_proc)]
        start = 0
        for i in range(n_proc//2):
            final = math.ceil(len(self.urls) / (n_proc // 2) * (i+1))
            processes[i] = multiprocessing.Process(target=self.parse_corpus,
                                                   args=('tajik', result, i, start, final))
            processes[i+n_proc//2] = multiprocessing.Process(target=self.parse_corpus,
                                                             args=('farsi', result,
                                                                   i+n_proc//2, start, final))
            start = final
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        return result

    @staticmethod
    def sentences_to_csv(result):
        result_t = []
        result_f = []
        for i in range(len(result)):
            if i < multiprocessing.cpu_count()//2:
                result_t += result[i]
            else:
                result_f += result[i]
        tajik = pd.DataFrame({'tajik': list(result_t)})
        farsi = pd.DataFrame({'farsi': list(result_f)})
        tajik.to_csv('tajik.csv', index=False)
        farsi.to_csv('farsi.csv', index=False)
