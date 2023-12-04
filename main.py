import re
import json
import pandas as pd
import argparse
import logging
import sys
from scipy.spatial.distance import cosine

DATA_PATH = 'data/'
CACHE_PATH = '.cache/'

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))

C = 60

DF_VECTORS: pd.DataFrame = pd.read_csv(DATA_PATH + 'index.csv', index_col=0)


def rank_articles(article_title: str, other_articles: list[str]) -> list[str]:
    """
    Rank the articles based on the given article title.

    :param article_title: Title of the article to rank.
    :type article_title: str
    :param other_articles: List of articles to rank.
    :type other_articles: list[str]

    :return: List of ranked articles.
    :rtype: list[str]
    """
    article_vector = DF_VECTORS.loc[article_title]
    other_articles_vectors = DF_VECTORS.loc[other_articles]
    similarities = other_articles_vectors.apply(lambda x: 1 - cosine(x, article_vector), axis=1)
    similarities = similarities.sort_values(ascending=False)

    articles = similarities.index.tolist()

    return articles


def reciprocal_rank(ranked_articles_lists: list[list[str]], k: int) -> list[str]:
    if len(ranked_articles_lists) == 0:
        return []

    all_articles = set()
    weight = 1 / len(ranked_articles_lists)

    for ranked_articles_list in ranked_articles_lists:
        for article in ranked_articles_list:
            all_articles.add(article)

    rrf_score_dic = {doc: 0.0 for doc in all_articles}

    for ranked_articles_list in ranked_articles_lists:
        for rank, article in enumerate(ranked_articles_list):
            rrf_score_dic[article] += 1 / ((rank + 1) * weight)

    sorted_rrf_score_dic = sorted(rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True)

    return sorted_rrf_score_dic[:k] if k < len(sorted_rrf_score_dic) else sorted_rrf_score_dic


def main() -> None:
    parser = argparse.ArgumentParser(description='Recommend articles based on a given article.')
    parser.add_argument('history', type=str, help='Path to the history file.')
    parser.add_argument('-k', '--k', type=int, help='Number of articles to return.', required=False, default=10)
    parser.add_argument('-o', '--output', type=str, help='Path to the output file.', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.', required=False)

    args = parser.parse_args()
    history_path: str = args.history
    output_path: str | None = args.output
    k: int = args.k
    verbose: bool = args.verbose

    if verbose:
        LOGGER.setLevel(logging.INFO)
    else:
        LOGGER.setLevel(logging.WARNING)

    LOGGER.info(f'Starting recommendation based on {history_path}...')

    with open(history_path, 'r') as f:
        history = json.load(f)

    LOGGER.info('Loaded history.')

    LOGGER.info('Ranking articles...')

    all_articles = set(DF_VECTORS.index.tolist())   # get all articles from the index
    history = [article for article in history if article in all_articles]   # filter out articles from the history
    other_articles = [article for article in all_articles if article not in history]  # get the other articles
    ranked_articles_lists = [rank_articles(article, other_articles) for article in history]    # rank the articles
    ranked_articles = reciprocal_rank(ranked_articles_lists, k)    # combine the rankings and get the top k articles

    LOGGER.info('Ranked articles.')

    if output_path:
        LOGGER.info(f'Saving ranked articles to {output_path}...')

        with open(output_path, 'w') as f:
            json.dump(ranked_articles, f)

        LOGGER.info('Saved ranked articles.')
    else:
        print(ranked_articles)


if __name__ == '__main__':
    main()
