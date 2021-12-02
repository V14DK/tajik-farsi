from parsering import Parser


def main():
    parser = Parser('corpus.csv')
    result = {0: []}
    parser.parse_corpus(0, 0, result) #0, 0 - ни на что не влияют, просто пока пусть будет так
    print(result[0]['tajik'])
    print(result[0]['farsi'])


if __name__ == "__main__":
    main()
