import sys
import pandas as pd
import nltk
import re
import logging

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

DATA_PATH = 'data/'
CACHE_PATH = '.cache/'

nltk.download('punkt', download_dir=CACHE_PATH)
nltk.download('stopwords', download_dir=CACHE_PATH)
nltk.download('wordnet', download_dir=CACHE_PATH)

nltk.data.path.append(CACHE_PATH)

STOP_WORDS = set(stopwords.words('english'))
STEMMER = PorterStemmer()

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


def preprocess(text: str) -> str:
    """
    Preprocess text by removing stop words and lemmatizing.

    :param text: Text to preprocess.
    :type text: str

    :return: Preprocessed text.
    :rtype: str
    """
    text = re.sub(r'\[[0-9]+\]', '', text)
    text = re.sub(r'\[[a-zA-Z]+\]', '', text)
    text = re.sub(r'notes$', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()

    tokens = word_tokenize(text)
    tokens = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS]

    return ' '.join(tokens)


def main() -> None:
    """
    Preprocess the data and save it to a new file.
    """
    LOGGER.info(f'Starting preprocessing {DATA_PATH}articles.csv...')

    df = pd.read_csv(DATA_PATH + 'articles.csv')

    LOGGER.info('Loaded data.')
    LOGGER.info('Preprocessing data...')

    df['article'] = df['article'].apply(preprocess)

    LOGGER.info('Preprocessed data.')
    LOGGER.info('Saving preprocessed data...')

    df.to_csv(DATA_PATH + 'articles_preprocessed.csv', index=False)

    LOGGER.info('Saved preprocessed data.')
    LOGGER.info('Done.')


if __name__ == '__main__':
    main()
