# Copyright (c) [2020] [P.H.]

import random

# import keras
# import tensorflow as tf
# import tensorflow.keras.optimizers
# from keras.models import Sequential, load_model
# from keras.optimizer_v2 import gradient_descent
# import numpy as np
import numpy as np
import tensorflow as tf


class ModelConfig:
    def __init__(self):
        self.train_loop = 5
        self.batch_size = 32
        self.epochs = 3


class MyModel:
    def __init__(self, config, input_shape=(36, 36, 4), output_shape=(289)):
        self.input_shape = input_shape
        self.output_shape1 = 576  # the number of pi=2*6*6*8
        self.output_shape2 = 1  # the number of v
        self._build_model()
        self.config = config

    def loadModel(self, pathfile):
        m = tf.keras.models.load_model(
            pathfile)  # , custom_objects={'softmax_cross_entropy_with_logits': softmax_cross_entropy_with_logits})
        self.model.set_weights(m.get_weights())

    def writeModel(self, pathfile):
        self.model.save(pathfile)

    def getPredict(self, s):
        s = np.array([s])
        piv = self.model.predict(s)
        return [piv[0][0], piv[1][0][0]]  # it seems tf return [[1,pi],[1,v]]

    def evaluate(self, state, turn):
        a = self.state2input(state, turn)
        return self.getPredict(a)

    def state2input(self, state, turn):
        a = np.zeros((36, 36, 4), dtype=float)
        if turn == -1:
            turn = 0
        for i in range(6):
            for j in range(6):
                a[i, j, 0] = turn
                if state[i][j] == 1:  # white
                    a[i, j, 1] = 1
                elif state[i][j] == -1:  # black
                    a[i, j, 2] = 1
                else:
                    a[i, j, 3] = 2  # block
        return a

    # def _build_model(self):
    #     # sample_number=2
    #     # ainput=[]
    #     # aoutput=[]
    #     # for i in range(sample_number):
    #     #     ainput.append(np.arange(36*36*4,dtype=float).reshape(36,36,4))
    #     #     aoutput.append(np.arange(36*36*4,dtype=float).reshape(36,36,4))
    #     self.model = tf.keras.models.Sequential()
    #     x = keras.layers.Conv2D(8, (3, 3), input_shape=self.input_shape, padding='SAME')
    #     self.model.add(x)
    #     # self.model.add(keras.layers.Dense(units=8, activation='relu'))
    #     self.model.add(keras.layers.Flatten())
    #     self.model.add(keras.layers.Dense(units=577, activation='sigmoid'))
    #     sgd = tf.keras.optimizers.SGD(lr=0.01)
    #     self.model.compile(loss='categorical_crossentropy', optimizer=sgd)
    #     print(self.model.summary())
    def _compute_gradients(tensor, var_list):
        grads = tf.gradients(tensor, var_list)
        return [grad if grad is not None else tf.zeros_like(var) for var, grad in zip(var_list, grads)]

    def _build_model(self):
        def convolutional_block(x, filter):
            # copy tensor to variable called x_skip
            x_skip = x
            # Layer 1
            x = tf.keras.layers.Conv2D(filter, (3, 3), padding='same', strides=(2, 2))(x)
            x = tf.keras.layers.BatchNormalization(axis=3)(x)
            x = tf.keras.layers.Activation('relu')(x)
            # Layer 2
            x = tf.keras.layers.Conv2D(filter, (3, 3), padding='same')(x)
            x = tf.keras.layers.BatchNormalization(axis=3)(x)
            # Processing Residue with conv(1,1)
            x_skip = tf.keras.layers.Conv2D(filter, (1, 1), strides=(2, 2))(x_skip)
            # Add Residue
            x = tf.keras.layers.Add()([x, x_skip])
            x = tf.keras.layers.Activation('relu')(x)
            return x

        def identity_block(x, filter):
            # copy tensor to variable called x_skip
            x_skip = x
            # Layer 1
            x = tf.keras.layers.Conv2D(filter, (3, 3), padding='same')(x)
            x = tf.keras.layers.BatchNormalization(axis=3)(x)
            x = tf.keras.layers.Activation('relu')(x)
            # Layer 2
            x = tf.keras.layers.Conv2D(filter, (3, 3), padding='same')(x)
            x = tf.keras.layers.BatchNormalization(axis=3)(x)
            # Add Residue
            x = tf.keras.layers.Add()([x, x_skip])
            x = tf.keras.layers.Activation('relu')(x)
            return x

        # Step 1 (Setup Input Layer)
        x_input = tf.keras.layers.Input(self.input_shape)
        x = tf.keras.layers.ZeroPadding2D((3, 3))(x_input)
        # Step 2 (Initial Conv layer along with maxPool)
        x = tf.keras.layers.Conv2D(64, kernel_size=7, strides=2, padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('relu')(x)
        x = tf.keras.layers.MaxPool2D(pool_size=3, strides=2, padding='same')(x)
        # Define size of sub-blocks and initial filter size
        block_layers = [3, 4, 6, 3]
        filter_size = 64
        # Step 3 Add the Resnet Blocks
        for i in range(1):
            if i == 0:
                # For sub-block 1 Residual/Convolutional block not needed
                for j in range(block_layers[i]):
                    x = identity_block(x, filter_size)
            else:
                # One Residual/Convolutional Block followed by Identity blocks
                # The filter size will go on increasing by a factor of 2
                filter_size = filter_size * 2
                x = convolutional_block(x, filter_size)
                for j in range(block_layers[i] - 1):
                    x = identity_block(x, filter_size)
        # Step 4 End Dense Network
        x = tf.keras.layers.AveragePooling2D((2, 2), padding='same')(x)
        x = tf.keras.layers.Flatten()(x)

        # **** part II starts here ****
        # x = tf.keras.layers.Dense(577, activation='relu')(x)
        pi_head = tf.keras.layers.Dense(self.output_shape1, activation='relu', name="pi_head")(x)
        v_head = tf.keras.layers.Dense(self.output_shape2, activation='softmax', name="v_head")(x)
        self.model = tf.keras.models.Model(inputs=x_input, outputs=[pi_head, v_head], name="ResNet_1_2")
        self.model.compile(
            loss={"pi_head": "categorical_crossentropy", "v_head": "mean_squared_error"},
            optimizer="sgd",
            loss_weights={"pi_head": 1, "v_head": 1},
            run_eagerly=True  # enable tensor.numpy()
        )
        # self.model.compile(loss='categorical_crossentropy', optimizer="sgd", loss_weights={"pi_head": 1, "v_head": 1})
        return

    # return [array of stepn [array of 2[nparray of 576 , nparray of 1]]] x
    # return [nparray of stepn [nparray of 576 or nparray of 1]] 
    def loss_function_AmazonChess(self, y_true, y_pred):
        # ***********************
        # print("************************** y_true.shape: ", y_true.shape)
        # print("************************** y_pred.shape: ", y_pred.shape)
        # print("************************** y_true: ", y_true.numpy())
        # print("************************** y_pred: ", y_pred.numpy())
        # print("************************** loss: ", (y_true - y_pred).numpy())
        ret_array = (y_true - y_pred).numpy()
        ret_array = ret_array * ret_array
        # print("************************** ret_array: ", ret_array)

        # y_true_pi=y_true[:-1]
        # y_true_v=y_true[-1]
        # y_pred_pi=y_pred[:-1]
        # y_pred_v=y_pred[-1]
        # loss=(y_true_v-y_pred_v)**2
        # loss+=tf.keras.losses.categorical_crossentropy(y_true_pi,y_pred_pi)
        return ret_array

    def train(self, memory):
        n = len(memory)
        for i in range(self.config.train_loop):
            batch_size = min(self.config.batch_size, n)
            sample = random.sample(memory, batch_size)
            states = []
            # piv=np.array([])
            # piv = []
            pi = []
            v = []
            turn = []
            for j in range(batch_size):
                states.append(sample[j][0])
                # piv.append(sample[j][1])
                pi.append(sample[j][1][0:576])
                v.append(sample[j][1][576])
                turn.append(sample[j][2])

            x = []

            for j in range(batch_size):
                x.append(self.state2input(states[j], turn[j]))
            x = np.asarray(x).astype('float32')

            # y = np.asarray(piv).astype('float32')
            pi = np.asarray(pi).astype('float32')
            v = np.asarray([[j] for j in v]).astype('float32')  # v=[0,1] -> [[0],[1]]
            piv = [pi, v]

            # -------------- cmd command: python -m tensorboard.main --logdir=logs ------------------------
            # logdir="./logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            # tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)
            self.model.fit(x=x, y={"pi_head": pi, "v_head": v}, epochs=self.config.epochs, verbose=1,
                           batch_size=batch_size)
            # callbacks=[tensorboard_callback])

            # print(var.history)
            return


if __name__ == "__main__":
    # output_dim=[289] #36*8+1
    MyModel(ModelConfig())
