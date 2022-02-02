import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.backend import int_shape

def bpnet_seq(inputlen=2114, outputlen=1000, filters=512, ndil=8):
    """
    Classic BPNet architecture with sequence-only input. Predicts profile
    logits and log-counts.

    Inputs and outputs have length inputlen and outputlen respectively.
    """

    inp = keras.Input((inputlen,4))

    x = keras.layers.Conv1D(filters,
                            kernel_size=21,
                            padding='valid',
                            activation='relu')(inp)

    for i in range(1, ndil+1):
        conv_x = keras.layers.Conv1D(filters,
                                     kernel_size=3,
                                     padding='valid',
                                     activation='relu',
                                     dilation_rate=2**i)(x)

        x_len = int_shape(x)[1]
        conv_x_len = int_shape(conv_x)[1]

        assert((x_len - conv_x_len) % 2 == 0) # Necessary for symmetric cropping

        x = keras.layers.Cropping1D((x_len - conv_x_len) // 2)(x)
        x = keras.layers.add([conv_x, x])

    prof = keras.layers.Conv1D(1, 75, padding='valid')(x)
    prof = keras.layers.Flatten(name="logits")(prof)
    assert prof.shape[1] == outputlen, prof.shape[1]

    ct = keras.layers.GlobalAvgPool1D()(x)
    ct = keras.layers.Dense(1, name="logcounts")(ct)

    return keras.Model(inputs=inp, outputs=[prof,ct])

