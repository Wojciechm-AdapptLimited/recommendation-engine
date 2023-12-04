from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import logging
import sys
from joblib import dump

DATA_PATH = 'data/'

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


def main() -> None:
    """
    Build the index of the articles.
    """
    LOGGER.info(f'Building index from {DATA_PATH}articles_preprocessed.csv...')

    df = pd.read_csv(DATA_PATH + 'articles_preprocessed.csv')

    LOGGER.info('Loaded data.')
    LOGGER.info('Building index...')

    vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=False)
    vectors = vectorizer.fit_transform(df['article'])

    LOGGER.info('Built index.')
    LOGGER.info('Saving index...')

    dump(vectorizer, DATA_PATH + 'vectorizer.joblib')
    df_vectors = pd.DataFrame(vectors.toarray(), columns=vectorizer.get_feature_names_out(), index=df['title'])
    df_vectors.to_csv(DATA_PATH + 'index.csv')

    LOGGER.info('Saved index.')
    LOGGER.info('Done.')


if __name__ == '__main__':
    main()
