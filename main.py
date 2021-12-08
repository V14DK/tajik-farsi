from parsing import Parser


def main():
    parser = Parser('corpus.csv')
    parser.sentences_to_csv(parser._get_sentences())


if __name__ == "__main__":
    main()
