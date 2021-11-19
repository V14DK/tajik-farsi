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

    def __parse_text_to_sentences(self, url, result):
        sentences = self.__parse_html_to_text(url)
        if 'tajik' in url:
            sentences = [s for s in sentences.rstrip().lstrip().split('.') if s]
            result[0] += sentences
            print('tajik = ', len(result[0]))
        else:
            my_normalizer = Normalizer()
            my_tokenizer = Tokenizer()
            sentences = my_tokenizer.tokenize_sentences(my_normalizer.normalize(sentences))
            result[1] += sentences
            print('farsi = ', len(result[1]))

    def parse_corpus(self, language, result):
        for i in range(len(self.urls)):
            self.__parse_text_to_sentences(self.urls[language + ' url'][i], result)

    def get_sentences(self):
        manager = multiprocessing.Manager()
        result = manager.list([manager.list(), manager.list()])
        processes = [
                        multiprocessing.Process(target=self.parse_corpus, args=('tajik', result)),
                        multiprocessing.Process(target=self.parse_corpus, args=('farsi', result))
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        return result
