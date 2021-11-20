import time
from parsering import Parser


def main():
    parser = Parser('corpus.csv')
    t = time.time()
    sentences = parser.get_sentences()
    parser.sentences_to_csv(sentences)
    print(time.time() - t)


if __name__ == "__main__":
    main()
