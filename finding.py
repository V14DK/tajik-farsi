import string
from parsivar import Tokenizer


class Finder:
    def __init__(self):
        self.punc = r'!#()*,-./:[]«»،ء؛؟۰۱۲۳۴۵۶۷۸۹…$﷼َٔ?"'
        self.tokenizer = Tokenizer()
        self.languages = ['tajik', 'farsi']

    def __delete_existing(self, sentences, index):
        for lang in self.languages:
            sentences[lang] = [sentences[lang][i] for i in range(len(sentences[lang]))
                               if i not in index[lang]]
        index = {'tajik': [], 'farsi': []}

    def __find_pairs(self, sentences, pairs, index):
        maxl = max(len(sentences['farsi']), len(sentences['tajik']))
        minl = min(len(sentences['farsi']), len(sentences['tajik']))
        for i in range(len(sentences['tajik'])):
            sen_t = sentences['tajik'][i]
            tbl_t = sen_t.maketrans('', '', string.punctuation)
            sen_t = sentences['tajik'][i].translate(tbl_t).split()
            for j in range(i, len(sentences['farsi'])):
                if j > i + maxl - minl:
                    break
                sen_f = sentences['farsi'][j]
                tbl_f = sen_f.maketrans({char: '' for char in self.punc})
                sen_f = self.tokenizer.tokenize_words(sentences['farsi'][j].translate(tbl_f))
                if (len(sen_t) <= len(sen_f) + 2) and (len(sen_t) >= len(sen_f) - 2) \
                        and sentences['tajik'][i] not in pairs['tajik'] \
                        and sentences['farsi'][j] not in pairs['farsi']:
                    pairs['tajik'].append(sentences['tajik'][i])
                    pairs['farsi'].append(sentences['farsi'][j])
                    index['tajik'].append(i)
                    index['farsi'].append(j)
                    break
        self.__delete_existing(sentences, index)

    def find_pairs(self, sentences):
        pairs = {'tajik': [], 'farsi': []}
        index = {'tajik': [], 'farsi': []}
        self.__find_pairs(sentences, pairs, index)
        return pairs
