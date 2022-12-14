import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow.keras import callbacks
from tensorflow.keras import optimizers


def train_model(model: tf.keras.Model, name: str, path_component: str, X_train: np.ndarray, y_train: np.ndarray,
                X_val: np.ndarray, y_val: np.ndarray, lr: float = 0.001, train: bool = True, n_epochs: int = 1000,
                verbose: int = 1, batch_size: int = 2048, lr_patience: int = None, es_patience: int = None,
                loss_weights: float = None):
    """
    Train a Keras model.
    :param model: Keras model
    :param name: model name used in weight paths
    :param path_component: component of the path for model weights and history. Usually the notebook name
    :param X_train:
    :param y_train:
    :param X_val:
    :param y_val:
    :param lr:
    :param train: if True: the model is trained and the weights and history are saved. If False, the weights and
    history are loaded
    :param n_epochs:
    :param verbose: verbosity during training
    :param batch_size:
    :param lr_patience: patience of ReduceLROnPlateau
    :param es_patience: patience of EarlyStopping
    :param loss_weights: loss function values can be multiplied by this weight
    :return: history dict
    """
    model.compile(loss='mse', optimizer=optimizers.Adam(lr), loss_weights=loss_weights)

    model_callbacks = [
        callbacks.ModelCheckpoint(filepath=f'model_weights/{path_component}/{name}/weights', save_best_only=True,
                                  save_weights_only=True)
    ]
    if es_patience is not None:
        model_callbacks.append(callbacks.EarlyStopping(patience=es_patience))
    if lr_patience is not None:
        model_callbacks.append(callbacks.ReduceLROnPlateau(monitor='loss', factor=0.5, patience=lr_patience))

    if train:
        history = model.fit(X_train, y_train, epochs=n_epochs, verbose=verbose, batch_size=batch_size,
                            validation_data=(X_val, y_val), callbacks=model_callbacks).history
        pd.DataFrame(history).to_csv(f'model_weights/{path_component}/{name}/loss_log.csv')

    model.load_weights(f'model_weights/{path_component}/{name}/weights')
    history = pd.read_csv(f'model_weights/{path_component}/{name}/loss_log.csv')

    return history


def plot_history(history: dict[str, np.array], title: str, ymax: float = None, figsize: tuple[float, float] = (8, 6)):
    plt.figure(figsize=figsize)

    X = np.arange(1, len(history['loss']) + 1)

    plt.plot(X, history['loss'], label='train')
    plt.plot(X, history['val_loss'], label='validation')

    if ymax is not None:
        plt.ylim(0, ymax)

    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.title(f"validation loss: {min(history[f'val_loss'].values):0.4f}")
    plt.grid()
    plt.legend()

    plt.suptitle(title)
    plt.show()
