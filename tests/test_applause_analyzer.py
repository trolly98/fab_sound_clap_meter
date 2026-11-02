import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fab_sound_clap_meter"))

import pytest

from applause_analyzer.applause_analyzer import ApplauseAnalyzer
from applause_analyzer.default_registry import build_default_registry
from applause_analyzer.percentile import percentile

DT = 0.05


def analyzer():
    registry = build_default_registry()
    return ApplauseAnalyzer(registry.create(registry.names()[0]))


def feed(a, scores_by_second):
    t = 0.0
    for duration, score in scores_by_second:
        for _ in range(round(duration / DT)):
            a.feed(t, score)
            t += DT
    return t


def test_registry_has_weighted_sliding_window():
    assert "Weighted Sliding Window Algorithm" in build_default_registry().names()


def test_percentile():
    assert percentile([1, 2, 3, 4, 5], 0.9) == pytest.approx(4.6)


def test_stopped_by_default_and_ignores_input():
    a = analyzer()
    a.feed(0.0, 9.0)
    assert not a.running and a.live_score == 1.0


def test_steady_loud_applause():
    a = analyzer()
    a.start(0.0)
    feed(a, [(6.0, 8.0)])
    assert a.live_score == pytest.approx(8.4, abs=0.05)   # 0.5*8 + 0.3*8 + 0.2*10


def test_stays_at_one_until_activation_threshold():
    a = analyzer()
    a.start(0.0)
    feed(a, [(3.0, 2.0)])
    assert a.live_score == 1.0


def test_window_slides_and_forgets_old_applause():
    a = analyzer()
    a.start(0.0)
    feed(a, [(4.0, 9.0), (5.0, 2.0)])
    assert a.live_score < 2.0   # 0.5*2 + 0.3*2 + 0.2*1


def test_final_score_is_average_of_last_seconds():
    a = analyzer()
    a.start(0.0)
    feed(a, [(5.0, 8.0), (2.5, 4.0)])
    live_before_stop = a.live_score
    a.stop()
    assert not a.running
    assert live_before_stop < a.final_score < 8.4   # media degli ultimi 2,5 s, non l'ultimo istante


def test_weights_are_normalised():
    registry = build_default_registry()
    algo = registry.create(registry.names()[0])
    algo.set_value("weight_mean", 100); algo.set_value("weight_peak", 0); algo.set_value("weight_constancy", 0)
    a = ApplauseAnalyzer(algo)
    a.start(0.0)
    feed(a, [(6.0, 7.0)])
    assert a.live_score == pytest.approx(7.0, abs=0.05)


def test_only_window_length_is_basic_everything_else_is_advanced():
    registry = build_default_registry()
    parameters = registry.create(registry.names()[0]).describe_parameters()
    basic = [p["key"] for p in parameters if not p["advanced"]]
    assert basic == ["window_s"]
    assert len(parameters) == 8
