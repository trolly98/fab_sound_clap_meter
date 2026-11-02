import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fab_sound_clap_meter"))

from domain.score_extremes import ScoreExtremes
from domain.spike_filter import SpikeFilter

BASE = -50.0
MAX_SPIKE, QUIET, THRESHOLD = 6, 4, 12.0       # 300 ms, 200 ms, 12 dB


def signal(offsets, pre=30, post=30):
    rnd = random.Random(1)
    return [BASE + o + rnd.uniform(-1.5, 1.5) for o in [0.0] * pre + list(offsets) + [0.0] * post]


def run(samples):
    f = SpikeFilter(MAX_SPIKE, QUIET, THRESHOLD)
    return [f.filter(x) for x in samples]


def peak_above_base(offsets):
    return max(run(signal(offsets))) - BASE


# ---- cose da togliere ----
def test_short_knock_is_removed():
    assert peak_above_base([30, 12]) < 3


def test_clap_with_decay_tail_is_removed():
    assert peak_above_base([40, 34, 28, 22, 16, 10, 4]) < 6


def test_shout_up_to_max_duration_is_removed():
    assert peak_above_base([25] * MAX_SPIKE) < 3


def test_double_knock_is_one_spike():
    assert peak_above_base([30, 0, 0, 30]) < 3


def test_spike_inside_applause_is_removed():
    out = run(signal([30] * 40 + [50, 50, 50] + [30] * 40))
    assert max(out) - BASE < 33


# ---- cose da lasciare intatte ----
def test_longer_shout_is_treated_as_applause():
    assert peak_above_base([25] * (MAX_SPIKE + 2)) > 20


def test_sudden_applause_is_kept_entirely():
    out = run(signal([30] * 60))
    assert sum(v > BASE + 20 for v in out) == 60


def test_gradual_applause_is_kept_entirely():
    out = run(signal([i * 1.5 for i in range(20)] + [30] * 40))
    assert sum(v > BASE + 20 for v in out) == 46


def test_dense_claps_are_kept():
    out = run(signal([25, 0, 0] * 14))
    assert sum(v > BASE + 15 for v in out) == 14


def test_plain_noise_is_untouched():
    samples = signal([])
    assert run(samples)[-30:] == samples[-40:-10]    # solo ritardato di 10 campioni


def test_extremes_track_min_and_max():
    e = ScoreExtremes()
    assert (e.minimum, e.maximum) == (1.0, 1.0)
    for s in (4.0, 7.5, 2.5):
        e.update(s)
    assert (e.minimum, e.maximum) == (2.5, 7.5)
    e.reset()
    assert (e.minimum, e.maximum) == (1.0, 1.0)
