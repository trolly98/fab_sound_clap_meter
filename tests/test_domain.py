import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fab_sound_clap_meter"))

from domain.calibration_mode import CalibrationMode
from domain.weighted_power_mixer import WeightedLevel, WeightedPowerMixer


def test_equal_levels_stay_equal():
    mixer = WeightedPowerMixer()
    assert math.isclose(mixer.mix([WeightedLevel(-30, 1), WeightedLevel(-30, 5)]), -30, abs_tol=1e-9)


def test_heavier_input_dominates():
    mixer = WeightedPowerMixer()
    mixed = mixer.mix([WeightedLevel(-20, 9), WeightedLevel(-50, 1)])
    assert -21 < mixed < -20


def test_zero_weight_is_ignored():
    assert WeightedPowerMixer().mix([WeightedLevel(-10, 0), WeightedLevel(-40, 2)]) == -40


def test_linear_mapping_endpoints():
    mapper = CalibrationMode.MANUAL.create_mapper(-60, -20, 2.0)
    assert mapper.map(-80) == 1.0 and mapper.map(-20) == 10.0 and mapper.map(0) == 10.0
    assert math.isclose(mapper.map(-40), 5.5)


def test_curve_is_stricter_on_low_values():
    linear = CalibrationMode.SIMPLE.create_mapper(-60, -20, 2.0)
    curved = CalibrationMode.CURVED.create_mapper(-60, -20, 2.0)
    assert curved.map(-40) < linear.map(-40)
