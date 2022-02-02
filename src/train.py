from tensorflow import keras
import tensorflow as tf
import archs
from utils import data_utils, train_utils, augment, argmanager
from utils.loss import multinomial_nll
import numpy as np
import random
import string
import math
import os
import json


def subsample_nonpeak_data(nonpeak_seqs, nonpeak_cts, peak_data_size, negative_sampling_ratio):
    #Randomly samples a portion of the non-peak data to use in training
    num_nonpeak_samples = int(negative_sampling_ratio * peak_data_size)
    nonpeak_indices_to_keep = np.random.choice(len(nonpeak_seqs), size=num_nonpeak_samples, replace=False)
    nonpeak_seqs = nonpeak_seqs[nonpeak_indices_to_keep]
    nonpeak_cts = nonpeak_cts[nonpeak_indices_to_keep]
    return nonpeak_seqs, nonpeak_cts


class BatchGenerator(keras.utils.Sequence):
    """
    This generator randomly crops (=jitter) and revcomps training examples for 
    every epoch 
    """
    def __init__(self, peak_seqs, nonpeak_seqs, peak_cts, nonpeak_cts, negative_sampling, negative_sampling_ratio, inputlen, outputlen, batch_size):
        """
        seqs: B x L' x 4
        cts: B x M'
        inputlen: int (L <= L'), L' is greater to allow for cropping (= jittering)
        outputlen: int (M <= M'), M' is greater to allow for cropping (= jittering)
        batch_size: int (B)
        """

        self.peak_seqs, self.nonpeak_seqs = peak_seqs, nonpeak_seqs
        self.peak_cts, self.nonpeak_cts = peak_cts, nonpeak_cts
        self.negative_sampling = negative_sampling
        self.negative_sampling_ratio = negative_sampling_ratio
        self.inputlen = inputlen
        self.outputlen = outputlen
        self.batch_size = batch_size

        # random crop training data to the desired sizes, revcomp augmentation
        self.crop_revcomp_data()

    def __len__(self):
        return math.ceil(self.seqs.shape[0]/self.batch_size)

    def crop_revcomp_data(self):
        # random crop training data to inputlen and outputlen (with corresponding offsets), revcomp augmentation
        # shuffle required since otherwise peaks and nonpeaks will be together

        #Sample a fraction of the negative samples according to the specified ratio
        if self.negative_sampling:
            self.sampled_nonpeak_seqs, self.sampled_nonpeak_cts = subsample_nonpeak_data(self.nonpeak_seqs, self.nonpeak_cts, len(self.peak_seqs), self.negative_sampling_ratio)
            self.seqs = np.vstack([self.peak_seqs, self.sampled_nonpeak_seqs])
            self.cts = np.vstack([self.peak_cts, self.sampled_nonpeak_cts])
        else:
            self.seqs = np.vstack([self.peak_seqs, self.nonpeak_seqs])
            self.cts = np.vstack([self.peak_cts, self.nonpeak_cts])

        self.cur_seqs, self.cur_cts = augment.crop_revcomp_augment(
                                         self.seqs, self.cts, self.inputlen, self.outputlen, 
                                         shuffle=True
                                      )

    def __getitem__(self, idx):
        batch_seq = self.cur_seqs[idx*self.batch_size:(idx+1)*self.batch_size]
        batch_cts = self.cur_cts[idx*self.batch_size:(idx+1)*self.batch_size]
        
        return batch_seq, [batch_cts, np.log(1+batch_cts.sum(-1, keepdims=True))] 

    def on_epoch_end(self):
        self.crop_revcomp_data()

def train_loop(model, inputlen, outputlen, train_peak_seqs, train_nonpeak_seqs, train_peak_cts, train_nonpeak_cts, 
               val_peak_seqs, val_nonpeak_seqs, val_peak_cts, val_nonpeak_cts, negative_sampling, negative_sampling_ratio, batch_size, epochs, early_stop, output_prefix): 

    if negative_sampling:
        np.random.seed(1248)
        val_nonpeak_seqs, val_nonpeak_cts = subsample_nonpeak_data(val_nonpeak_seqs, val_nonpeak_cts, len(val_peak_seqs), negative_sampling_ratio)
    val_seqs = np.vstack([val_peak_seqs, val_nonpeak_seqs])
    val_cts = np.vstack([val_peak_cts, val_nonpeak_cts])


    # need generator to crop and revcomp aug training examples, but not for 
    # validation. 
    train_generator = BatchGenerator(train_peak_seqs, train_nonpeak_seqs, 
                                               train_peak_cts, train_nonpeak_cts, negative_sampling, negative_sampling_ratio, inputlen, outputlen, batch_size)

    callbacks = train_utils.get_callbacks(early_stop, output_prefix)

    history = model.fit(train_generator, 
                        epochs=epochs,
                        validation_data=(val_seqs,
                                         [val_cts, 
                                          np.log(1+val_cts.sum(-1, keepdims=True))]),
                        callbacks=callbacks)

    return history

def main():
    args = argmanager.fetch_train_args()
    print(args)

    if os.path.exists("{}.h5".format(args.output_prefix)):
        raise OSError('File {}.h5 already exists'.format(args.output_prefix))

    # load data
    train_peaks_seqs, train_peaks_cts, train_nonpeaks_seqs, train_nonpeaks_cts,\
    val_peaks_seqs, val_peaks_cts, val_nonpeaks_seqs, val_nonpeaks_cts =  \
                            data_utils.load_train_val_data(
                                args.peaks, args.nonpeaks, args.genome, args.bigwig,
                                args.val_chr, args.test_chr, args.inputlen, args.outputlen, args.max_jitter,
                                outlier=0.9999
                            )

    # compute loss weight factor for counts loss
    counts_loss_weight = train_utils.get_counts_stat(train_peaks_cts,
                                     args.outputlen) * args.counts_weight
    print("\nCounts loss weight : {:.2f}\n".format(counts_loss_weight))

    # prepare  model
    model = archs.bpnet_seq(args.inputlen, args.outputlen, args.filters, args.ndil)
    opt = keras.optimizers.Adam(learning_rate=args.learning_rate)
    model.compile(
            optimizer=opt,
            loss=[multinomial_nll, 'mse'],
            loss_weights = [1, counts_loss_weight]
        )

    history = train_loop(model, args.inputlen, args.outputlen, 
                         train_peaks_seqs, train_nonpeaks_seqs,
                         train_peaks_cts, train_nonpeaks_cts,
                         val_peaks_seqs, val_nonpeaks_seqs,
                         val_peaks_cts, val_nonpeaks_cts, args.negative_sampling, args.negative_sampling_ratio,
                         args.batch_size, args.epochs, 
                         args.early_stop, args.output_prefix)

    with open("{}.history.json".format(args.output_prefix), "w") as f:
        json.dump(history.history, f, ensure_ascii=False, indent=4)

if __name__=="__main__":
    main()

