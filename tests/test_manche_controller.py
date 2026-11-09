import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fab_sound_clap_meter"))

import pytest

from application.applause_analyzer_controller import ApplauseAnalyzerController
from application.manche_controller import MancheController
from applause_analyzer.default_registry import build_default_registry
from infrastructure.json_race_store import JsonRaceStore
from manche.race import Race


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


@pytest.fixture
def setup(tmp_path):
    clock = FakeClock()
    applause = ApplauseAnalyzerController(build_default_registry(), clock=clock)
    store = JsonRaceStore(tmp_path / "race.json")
    manche = MancheController(Race(), store, applause)
    return manche, applause, clock, store


def run_for(applause, clock, seconds, score=8.0, has_input=True, dt=0.05):
    for _ in range(round(seconds / dt)):
        clock.now += dt
        applause.feed(score, has_input)


def votes(manche):
    return manche.view["run"]["slots"]


def test_manual_session_records_vote_with_two_decimals(setup):
    manche, applause, clock, store = setup
    assert manche.startMeasurement("new", False)
    assert manche.view["live"] and manche.view["locked"]
    run_for(applause, clock, 6.0)
    manche.stopMeasurement()
    first = votes(manche)[0]
    assert first["status"].startswith("✓") and not manche.view["live"]
    assert applause.final_score == pytest.approx(8.4, abs=0.05)
    assert first["status"] == "✓ " + f"{applause.final_score:.2f}".replace(".", ",")


def test_auto_session_stops_by_itself_after_the_set_duration(setup):
    manche, applause, clock, _ = setup
    applause.setSessionDurationS(4.0)
    assert manche.startMeasurement("new", True)
    assert applause.timed
    run_for(applause, clock, 3.0)
    assert manche.view["live"] and applause.remainingS == pytest.approx(1.0, abs=0.1)
    run_for(applause, clock, 1.2)
    assert not manche.view["live"] and votes(manche)[0]["status"].startswith("✓")
    assert manche.view["history"][0]["mode"] == "Ordinaria · automatica"


def test_session_without_input_is_empty_and_records_no_vote(setup):
    manche, applause, clock, _ = setup
    manche.startMeasurement("new", True)
    run_for(applause, clock, 11.0, score=1.0, has_input=False)
    assert votes(manche)[0]["status"] == "Vuota"
    assert manche.view["history"][0]["status"] == "Vuota" and manche.view["history"][0]["value"] == "—"


def test_cancelled_session_records_no_vote(setup):
    manche, applause, clock, _ = setup
    manche.startMeasurement("new", False)
    run_for(applause, clock, 2.0)
    manche.cancelMeasurement()
    assert votes(manche)[0]["status"] == "Annullata" and manche.view["run"]["slot"]["canStart"]


def test_stop_of_somebody_elses_session_is_ignored(setup):
    manche, applause, clock, _ = setup
    applause.start()                      # avviata fuori dalla gara (token vuoto)
    run_for(applause, clock, 2.0)
    applause.stop()
    assert not manche.view["live"] and not manche.view["history"]


def test_state_survives_restart(setup):
    manche, applause, clock, store = setup
    manche.startMeasurement("new", False)
    run_for(applause, clock, 5.0, score=7.0)
    manche.stopMeasurement()
    again = MancheController(Race.from_dict(store.load()), store, applause)
    assert again.view["run"]["slots"][0]["status"] == manche.view["run"]["slots"][0]["status"]


def test_full_flow_with_tie_break_through_controller(setup):
    manche, applause, clock, _ = setup
    while manche.view["run"]["nextTurn"]:
        manche.nextTurn()
        assert manche.startMeasurement("new", False)
        run_for(applause, clock, 6.0, score=8.0)
        manche.stopMeasurement()
    board = manche.view["board"]
    assert board["result"]["title"] in ("Pareggio finale",) or "in testa" in board["result"]["title"]


def test_config_edits_reach_the_view_and_are_locked_during_measure(setup):
    manche, applause, clock, _ = setup
    first = manche.view["config"]["rounds"][0]["id"]
    manche.selectConfigRound(first)
    manche.setRoundText(first, "name", "Prologo")
    assert manche.view["config"]["selected"]["name"] == "Prologo"
    assert manche.view["config"]["selected"]["turns"][0]["label"] == "A1"
    manche.startMeasurement("new", False)
    manche.setRoundText(first, "name", "Bloccato")
    assert manche.view["config"]["selected"]["name"] == "Prologo" and manche.view["lockReason"]
    manche.cancelMeasurement()
    assert not manche.view["canUndo"]               # avviare una misura azzera la cronologia di "Annulla"
    manche.undo()
    assert manche.view["config"]["selected"]["name"] == "Prologo"


def test_session_duration_is_clamped_and_saved(setup):
    manche, applause, _, _ = setup
    applause.setSessionDurationS(1000)
    assert applause.session_duration_s == 120
    applause.setSessionDurationS(0.1)
    assert applause.session_duration_s == 2
    applause.setSessionDurationS(15)
    assert applause.snapshot()["sessionDurationS"] == 15
