import difflib #это два простых компоратора, которые сравнивают отдельные токены,
from fuzzywuzzy import fuzz #не подходят для сопоставления предложений
from googletrans import Translator


class Finder:
    translator = Translator()

    @staticmethod
    def __delete_existing(sentences, trans, del_sen):
        #удаляются те предложения, которые друг другу сопоставлены
        languages = ['tajik', 'farsi']
        for lang in languages:
            sentences[lang] = [sentences[lang][i] for i in range(len(sentences[lang]))
                               if i not in del_sen[lang]]
            trans[lang] = [trans[lang][i] for i in range(len(trans[lang]))
                           if i not in del_sen[lang]]
        del_sen = {'tajik': [], 'farsi': []}

    @staticmethod
    def __find_pairs(sentences, trans, rating, pairs, del_sen):
        #сюда нужно вместо fuzz или difflib встроить нейронку, ratio поменять
        #проходимся двойным циклом по списку, худшая сложность O(i*j)
        for i in range(len(trans['tajik'])):
            for j in range(i, len(trans['farsi'])):
                ratio = fuzz.WRatio(trans['tajik'][i], trans['farsi'][j]) / 100
                if ratio >= 0.7:
                    rating.append(ratio)
                    pairs['tajik'].append(sentences['tajik'][i])
                    pairs['farsi'].append(sentences['farsi'][j])
                    del_sen['tajik'].append(i)
                    del_sen['farsi'].append(j)
                    break

    @staticmethod
    def find_pairs(sentences):
        trans = {'tajik': [], 'farsi': []}
        pairs = {'tajik': [], 'farsi': []}
        for sen in sentences['tajik']:
            trans['tajik'].append(Finder.translator.translate(sen).text)
        for sen in sentences['farsi']:
            trans['farsi'].append(Finder.translator.translate(sen).text)
        rating = []
        del_sen = {'tajik': [], 'farsi': []}
        Finder.__find_pairs(sentences, trans, rating, pairs, del_sen)
        Finder.__delete_existing(sentences, trans, del_sen)
        Finder.__find_pairs(sentences, trans, rating, pairs, del_sen)
        return pairs
