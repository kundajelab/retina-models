import tensorflow as tf
from tensorflow import keras
from utils import data_utils, argmanager
from utils.loss import multinomial_nll
import numpy as np
import os
import json
import scipy
import sklearn.metrics
import scipy.stats
from collections import OrderedDict


def softmax(x, temp=1):
    norm_x = x - np.mean(x,axis=1, keepdims=True)
    return np.exp(temp*norm_x)/np.sum(np.exp(temp*norm_x), axis=1, keepdims=True)


def get_jsd(preds, cts, min_tot_cts=10):
    return np.array([scipy.spatial.distance.jensenshannon(x,y) for x,y in zip(preds, cts) \
                     if y.sum()>min_tot_cts])


def main():
    args = argmanager.fetch_metrics_args()
    print(args)

    # load model
    with keras.utils.CustomObjectScope({'multinomial_nll':multinomial_nll, 'tf':tf}):
        model = keras.models.load_model(args.model)
    inputlen = int(model.input_shape[1])
    outputlen = int(model.output_shape[0][1])

    # load data
    test_peaks_seqs, test_peaks_cts, \
    test_nonpeaks_seqs, test_nonpeaks_cts = data_utils.load_test_data(
                            args.peaks, args.nonpeaks, args.genome, args.bigwig,
                            args.test_chr, inputlen, outputlen
                           )

    # predict on peaks and nonpeaks
    test_peaks_pred_logits, test_peaks_pred_logcts = \
            model.predict(test_peaks_seqs, 
                          batch_size=args.batch_size,
                          verbose=True)
    test_nonpeaks_pred_logits, test_nonpeaks_pred_logcts = \
            model.predict(test_nonpeaks_seqs, 
                          batch_size=args.batch_size,
                          verbose=True)

    metrics = OrderedDict()

    # counts metrics
    all_test_logcts = np.log(1 + np.vstack([test_peaks_cts, test_nonpeaks_cts]).sum(-1))
    cur_pair = (all_test_logcts,
                np.vstack([test_peaks_pred_logcts,
                           test_nonpeaks_pred_logcts]).ravel())
    metrics['chrombpnet_cts_pearson_peaks_nonpeaks'] = scipy.stats.pearsonr(*cur_pair)[0]
    metrics['chrombpnet_cts_spearman_peaks_nonpeaks'] = scipy.stats.spearmanr(*cur_pair)[0]

    cur_pair = ([1]*len(test_peaks_pred_logcts) + [0]*len(test_nonpeaks_pred_logcts), 
                 np.vstack([test_peaks_pred_logcts,
                           test_nonpeaks_pred_logcts]).ravel())                           
    metrics['binary_auc'] = sklearn.metrics.roc_auc_score(*cur_pair)

    peaks_test_logcts = np.log(1 + test_peaks_cts.sum(-1))
    cur_pair = (peaks_test_logcts, test_peaks_pred_logcts.ravel())
    metrics['chrombpnet_cts_pearson_peaks'] =  scipy.stats.pearsonr(*cur_pair)[0]
    metrics['chrombpnet_cts_spearman_peaks'] = scipy.stats.spearmanr(*cur_pair)[0]

    # profile metrics (all within peaks)
    cur_pair = (softmax(test_peaks_pred_logits), test_peaks_cts)
    metrics['chrombpnet_profile_median_jsd_peaks'] = np.median(get_jsd(*cur_pair)) 

    cur_pair = (softmax(test_peaks_pred_logits), 
                test_peaks_cts[:, np.random.permutation(test_peaks_cts.shape[1])])
    metrics['chrombpnet_profile_median_jsd_peaks_randomized'] = np.median(get_jsd(*cur_pair))

    with open(args.output_prefix + ".metrics.json", "w") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)

if __name__=="__main__":
    main()

