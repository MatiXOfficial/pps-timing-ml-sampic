import math
from collections import defaultdict
from pathlib import Path

from matplotlib import pyplot as plt

PLANES = [1, 2, 3]
PLANE_0 = 1
N_PLANES = 3

PlaneChannel = tuple[int, int]


def save_plt(path: Path | str, **kwargs) -> None:
    if isinstance(path, str):
        path = Path(path)
    path.parents[0].mkdir(parents=True, exist_ok=True)
    plt.savefig(path, **kwargs)


def _sorted_pair(a, b):
    return (a, b) if b > a else (b, a)


def deconvolve_precision(p: int, prec_dict: dict[PlaneChannel, float]) -> float:
    """
    sigma(1)^2 = sigma(1, 2)^2 + sigma(1, 3)^2 - sigma(2, 3)^2
    """
    p1 = (p - PLANE_0 + 1) % N_PLANES + PLANE_0
    p2 = (p - PLANE_0 + 2) % N_PLANES + PLANE_0

    pos_pair_1 = prec_dict[_sorted_pair(p, p1)]
    pos_pair_2 = prec_dict[_sorted_pair(p, p2)]
    neg_pair = prec_dict[_sorted_pair(p1, p2)]

    return math.sqrt(pos_pair_1 ** 2 + pos_pair_2 ** 2 - neg_pair ** 2)


def print_pairwise_precisions(precisions: dict[tuple[PlaneChannel, PlaneChannel], float]) -> None:
    channel_mutual_precisions: dict[int, dict[PlaneChannel, float]] = defaultdict(dict)
    for ((x_p, x_ch), (y_p, y_ch)), precision in precisions.items():
        assert x_ch == y_ch
        channel_mutual_precisions[x_ch][(x_p, y_p)] = precision

    for ch, data in channel_mutual_precisions.items():
        for (p_1, p_2), prec in data.items():
            print(f'ch {ch:2}: (p{p_1} vs p{p_2}): {prec:0.2f} ps')
