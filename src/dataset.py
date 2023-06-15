import pickle
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

TIME_STEP = 1. / 7.695
X_TIME = np.arange(0, 24) * TIME_STEP
X_TIME_MAX = X_TIME[-1]

DATASET_ROOT_PATH = Path('data/dataset/dataset.pkl')
EXPANDED_DATASET_ROOT_PATH = Path('data/dataset/dataset_exp.pkl')


def load_dataset(pwd: Path, plane: int, channel: int) -> tuple[np.ndarray, np.ndarray]:
    with open(pwd / DATASET_ROOT_PATH, 'rb') as file:
        dataset = pickle.load(file)

    all_X, all_y = dataset[(plane, channel)][0], dataset[(plane, channel)][1]
    return all_X, all_y


def load_dataset_train_test(
        pwd: Path, plane: int, channel: int, test_size: float = 0.2, random_state: int = 42
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    all_X, all_y = load_dataset(pwd, plane, channel)
    x_train, x_test, y_train, y_test = train_test_split(all_X, all_y, test_size=test_size, random_state=random_state)
    return x_train, x_test, y_train, y_test


def load_dataset_train_val(
        pwd: Path, plane: int, channel: int, test_size: float = 0.2, random_state: int = 42
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_base_train, _, y_base_train, _ = load_dataset_train_test(pwd, plane, channel)
    x_train, x_val, y_train, y_val = train_test_split(x_base_train, y_base_train, test_size=test_size,
                                                      random_state=random_state)
    return x_train, x_val, y_train, y_val


def load_dataset_all_channels(pwd: Path) -> tuple[dict[tuple, np.ndarray], dict[tuple, np.ndarray]]:
    with open(pwd / DATASET_ROOT_PATH, 'rb') as file:
        dataset = pickle.load(file)

    all_X, all_y = {}, {}
    for (plane, channel), (x, y) in dataset.items():
        all_X[(plane, channel)] = x
        all_y[(plane, channel)] = y
    return all_X, all_y


def load_dataset_train_test_all_channels(
        pwd: Path, test_size: float = 0.2, random_state: int = 42
) -> tuple[dict[tuple, np.ndarray], dict[tuple, np.ndarray], dict[tuple, np.ndarray], dict[tuple, np.ndarray]]:
    all_X, all_y = load_dataset_all_channels(pwd)

    x_train, x_test, y_train, y_test = {}, {}, {}, {}
    for (plane, channel), x in all_X.items():
        y = all_y[(plane, channel)]

        x_train_ch, x_test_ch, y_train_ch, y_test_ch = train_test_split(x, y, test_size=test_size,
                                                                        random_state=random_state)
        x_train[(plane, channel)] = x_train_ch
        x_test[(plane, channel)] = x_test_ch
        y_train[(plane, channel)] = y_train_ch
        y_test[(plane, channel)] = y_test_ch

    return x_train, x_test, y_train, y_test


def load_dataset_train_val_all_channels(
        pwd: Path, test_size: float = 0.2, random_state: int = 42
) -> tuple[dict[tuple, np.ndarray], dict[tuple, np.ndarray], dict[tuple, np.ndarray], dict[tuple, np.ndarray]]:
    all_X, _, all_y, _ = load_dataset_train_test_all_channels(pwd)

    x_train, x_val, y_train, y_val = {}, {}, {}, {}
    for (plane, channel), x in all_X.items():
        y = all_y[(plane, channel)]

        x_train_ch, x_val_ch, y_train_ch, y_val_ch = train_test_split(x, y, test_size=test_size,
                                                                      random_state=random_state)
        x_train[(plane, channel)] = x_train_ch
        x_val[(plane, channel)] = x_val_ch
        y_train[(plane, channel)] = y_train_ch
        y_val[(plane, channel)] = y_val_ch

    return x_train, x_val, y_train, y_val


def load_expanded_dataset(pwd: Path) -> tuple[np.ndarray, dict, dict, dict]:
    with open(pwd / EXPANDED_DATASET_ROOT_PATH, 'rb') as file:
        dataset = pickle.load(file)

    return dataset


def _extract_dataset_by_idx(
        dataset: tuple[np.ndarray, dict, dict, dict], idx: np.ndarray
) -> tuple[np.ndarray, dict, dict, dict]:
    dataset_t_cfd_avg, dataset_wav, dataset_t0, dataset_t_pred = dataset

    new_t_cfd_avg = dataset_t_cfd_avg[idx]
    new_wav, new_t0, new_t_pred = {}, {}, {}
    for key in dataset_wav.keys():
        new_wav[key] = dataset_wav[key][idx]
        new_t0[key] = dataset_t0[key][idx]
        new_t_pred[key] = dataset_t_pred[key][idx]

    return new_t_cfd_avg, new_wav, new_t0, new_t_pred


def load_expanded_dataset_train_test(
        pwd: Path, test_size: float = 0.2, random_state: int = 42
) -> tuple[tuple[np.ndarray, dict, dict, dict], tuple[np.ndarray, dict, dict, dict]]:
    dataset = load_expanded_dataset(pwd)
    train_idx, test_idx = train_test_split(np.arange(len(dataset[0])), test_size=test_size,
                                           random_state=random_state)

    train_dataset = _extract_dataset_by_idx(dataset, train_idx)
    test_dataset = _extract_dataset_by_idx(dataset, test_idx)
    return train_dataset, test_dataset


def load_expanded_dataset_train_val(
        pwd: Path, test_size: float = 0.2, random_state: int = 42
) -> tuple[tuple[np.ndarray, dict, dict, dict], tuple[np.ndarray, dict, dict, dict]]:
    dataset, _ = load_expanded_dataset_train_test(pwd, test_size, random_state)
    train_idx, val_idx = train_test_split(np.arange(len(dataset[0])), test_size=test_size,
                                          random_state=random_state)

    train_dataset = _extract_dataset_by_idx(dataset, train_idx)
    val_dataset = _extract_dataset_by_idx(dataset, val_idx)
    return train_dataset, val_dataset
