# See https://github.com/cytomining/copairs/issues/36 for details on why this file is needed

import itertools
import logging

import numpy as np
import pandas as pd

from copairs import compute
from copairs.map import create_matcher, build_rank_lists

logger = logging.getLogger("copairs")


def my_run_pipeline(
    meta,
    feats,
    pos_sameby,
    pos_diffby,
    neg_sameby,
    neg_diffby,
    null_size,
    batch_size=20000,
    seed=0,
) -> pd.DataFrame:
    # Critical!, otherwise the indexing wont work
    meta = meta.reset_index(drop=True).copy()
    logger.info("Indexing metadata...")
    matcher = create_matcher(meta, pos_sameby, pos_diffby, neg_sameby, neg_diffby)

    logger.info("Finding positive pairs...")
    pos_pairs = matcher.get_all_pairs(sameby=pos_sameby, diffby=pos_diffby)
    pos_total = sum(len(p) for p in pos_pairs.values())
    pos_pairs = np.fromiter(
        itertools.chain.from_iterable(pos_pairs.values()),
        dtype=np.dtype((np.int32, 2)),
        count=pos_total,
    )

    logger.info("Finding negative pairs...")
    neg_pairs = matcher.get_all_pairs(sameby=neg_sameby, diffby=neg_diffby)
    total_neg = sum(len(p) for p in neg_pairs.values())
    neg_pairs = np.fromiter(
        itertools.chain.from_iterable(neg_pairs.values()),
        dtype=np.dtype((np.int32, 2)),
        count=total_neg,
    )

    logger.info("Computing positive similarities...")
    pos_dists = compute.pairwise_cosine(feats, pos_pairs, batch_size)

    logger.info("Computing negative similarities...")
    neg_dists = compute.pairwise_cosine(feats, neg_pairs, batch_size)

    logger.info("Building rank lists...")
    rel_k_list, counts = build_rank_lists(pos_pairs, neg_pairs, pos_dists, neg_dists)

    logger.info("Computing average precision...")
    ap_scores, null_confs = compute.compute_ap_contiguos(rel_k_list, counts)

    logger.info("Computing p-values...")
    p_values = compute.compute_p_values(ap_scores, null_confs, null_size, seed=seed)

    logger.info("Creating result DataFrame...")
    meta["average_precision"] = ap_scores
    meta["p_value"] = p_values
    logger.info("Finished.")
    return meta, null_confs
