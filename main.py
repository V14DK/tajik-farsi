import pandas as pd
from parsering import Parser


def main():
    parser = Parser('corpus.csv')
    result = parser.get_sentences()
    dT = pd.DataFrame({'tajik': list(result[0])})
    dP = pd.DataFrame({'farsi': list(result[1])})
    dT.to_csv('farsi.csv', index=False)
    dP.to_csv('tajik.csv', index=False)
    print(pd.read_csv('farsi.csv'), pd.read_csv('tajik.csv'))


if __name__ == "__main__":
    main()
