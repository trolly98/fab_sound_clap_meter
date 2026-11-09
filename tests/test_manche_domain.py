import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fab_sound_clap_meter"))

import itertools

import pytest

from manche.entities import Round
from manche.race import Race
from manche.scoring import hundredth, round_points
from manche.sequence import sequence, slots


def make_race():
    counter = itertools.count(1)
    clock = itertools.count(1000)
    return Race(new_id=lambda: f"id{next(counter)}", now=lambda: float(next(clock)))


def rounds_by_name(race):
    return {r.name: r for r in race.game.rounds}


def record(race, rnd, values, mode="new"):
    """Registra i voti di tutti i turni della manche, nell'ordine."""
    for slot, value in zip(slots(rnd), values):
        session = race.begin_session(slot, mode)
        assert session is not None
        race.finish_session("valid", value)


# ---------------------------------------------------------------- sequenze
def test_sequences():
    r = Round("r", "x", count=2)
    assert sequence(r) == ["A", "B", "A", "B"]
    r.order = "consecutive"
    assert sequence(r) == ["A", "A", "B", "B"]
    r.order = "reverse"
    assert sequence(r) == ["A", "B", "B", "A"]


def test_slot_labels_follow_order_of_appearance():
    r = Round("r", "x", count=2, order="reverse")
    assert [s.label for s in slots(r)] == ["A1", "B1", "B2", "A2"]


def test_custom_sequence_is_completed_and_trimmed():
    r = Round("r", "x", count=2, order="custom", custom=["B", "B", "B", "A"])
    assert sequence(r) == ["B", "B", "A", "A"]          # B non supera il numero previsto


def test_new_round_defaults():
    race = make_race()
    new = race.add_round()
    assert (new.count, new.method, new.order, new.name) == (1, "mean", "alt", "Nuova manche")
    assert race.game.rounds[-1] is new


# ---------------------------------------------------------------- punteggi
def test_methods():
    race = make_race()
    r = rounds_by_name(race)["Il Tribunale"]
    race.set_count(r.id, 3)
    record(race, r, [6, 7, 8, 4, 9, 5])                  # A: 6,8,9  B: 7,4,5  (sequenza alternata)
    expectations = {"mean": (23 / 3, 16 / 3), "sum": (23, 16), "max": (9, 7), "last": (9, 5)}
    for method, (a, b) in expectations.items():
        race.game.result = None
        race.set_method(r.id, method)
        assert round_points(race.game, r, "A") == pytest.approx(a)
        assert round_points(race.game, r, "B") == pytest.approx(b)


def test_bazze_is_locked_and_averages_two_votes():
    race = make_race()
    bazze = rounds_by_name(race)["Bazze volanti"]
    assert not race.set_count(bazze.id, 3) and not race.set_method(bazze.id, "sum")
    record(race, bazze, [8, 6, 7, 9])                    # sequenza A1, B1, B2, A2
    assert round_points(race.game, bazze, "A") == pytest.approx(8.5)
    assert round_points(race.game, bazze, "B") == pytest.approx(6.5)


def test_points_missing_until_all_votes_present():
    race = make_race()
    bazze = rounds_by_name(race)["Bazze volanti"]
    record(race, bazze, [8, 6, 7])                       # manca A2
    assert round_points(race.game, bazze, "A") is None
    assert round_points(race.game, bazze, "B") == pytest.approx(6.5)


def test_hundredth_rounding():
    assert hundredth(8.345) == 8.35 and hundredth(8.344) == 8.34


# ---------------------------------------------------------------- gara completa, proclamazione, pareggio
def play_all(race, a_values, b_values):
    a, b = iter(a_values), iter(b_values)
    for rnd in race.game.rounds:
        for slot in slots(rnd):
            race.begin_session(slot, "new")
            race.finish_session("valid", next(a if slot.person == "A" else b))


def test_full_game_totals_and_winner():
    race = make_race()
    # A: bugio 8 | bazze (7+9)/2=8 | tribunale 6 | balla 8      B: 6 | (5+7)/2=6 | 9 | 8
    play_all(race, [8, 7, 9, 6, 8], [6, 5, 7, 9, 8])
    board = race.board()
    assert board.ready and board.done == 4
    assert [line.total["A"] for line in board.lines] == [8, 16, 22, 30]       # progressivi
    assert [line.total["B"] for line in board.lines] == [6, 12, 21, 29]
    assert board.total == {"A": 30, "B": 29} and board.lead == 1
    assert race.announce()
    assert (race.game.result.winner, race.game.result.via) == ("A", "gara")


def test_tie_flow_and_reopen():
    race = make_race()
    for rnd in race.game.rounds:
        for slot in slots(rnd):
            race.begin_session(slot, "new"); race.finish_session("valid", 7.0)
    board = race.board()
    assert board.ready and board.lead == 0
    assert race.start_tie() is not None
    assert race.board().tie_pending and not race.announce()
    tie = race.game.tie_rounds[-1]
    for slot, value in zip(slots(tie), [8.12, 8.11]):
        race.begin_session(slot, "new"); race.finish_session("valid", value)
    assert race.announce()
    assert (race.game.result.winner, race.game.result.via) == ("A", "spareggio")
    assert race.locked and not race.add_round()          # dopo la proclamazione la configurazione e' bloccata
    assert race.reopen() and not race.locked


def test_two_decimal_precision_decides_ties():
    race = make_race()
    for rnd in race.game.rounds:
        for slot in slots(rnd):
            race.begin_session(slot, "new"); race.finish_session("valid", 8.0 if slot.person == "A" else 8.0)
    assert race.board().lead == 0
    first = slots(race.game.rounds[0])[0]
    race.begin_session(first, "replace"); race.finish_session("valid", 8.01)
    assert race.board().lead == pytest.approx(0.01)


# ---------------------------------------------------------------- misure: esiti, sostituzione, straordinarie
def test_empty_and_cancelled_sessions_record_no_vote():
    race = make_race()
    slot = slots(race.game.rounds[0])[0]
    race.begin_session(slot, "new"); race.finish_session("empty", None)
    race.begin_session(slot, "new"); race.finish_session("cancelled", 5.0)
    assert race.vote(slot) is None
    assert [s.status for s in race.game.sessions] == ["empty", "cancelled"]
    assert all(s.value is None for s in race.game.sessions)


def test_value_one_is_a_valid_vote():
    race = make_race()
    slot = slots(race.game.rounds[0])[0]
    race.begin_session(slot, "new"); race.finish_session("valid", 1.0)
    assert race.vote(slot) == 1.0                         # 1,0 non e' "assenza di voto"


def test_replace_and_new_rules():
    race = make_race()
    slot = slots(race.game.rounds[0])[0]
    assert race.begin_session(slot, "replace") is None    # niente da sostituire
    race.begin_session(slot, "new"); race.finish_session("valid", 6.0)
    assert race.begin_session(slot, "new") is None        # il voto esiste gia'
    race.begin_session(slot, "replace"); race.finish_session("valid", 7.25)
    assert race.vote(slot) == 7.25


def test_extra_measure_enters_average_and_can_be_excluded():
    race = make_race()
    bugio = race.game.rounds[0]
    record(race, bugio, [6.0, 8.0])
    a_slot = slots(bugio)[0]
    race.begin_session(a_slot, "extra"); race.finish_session("valid", 10.0)
    assert round_points(race.game, bugio, "A") == pytest.approx(8.0)   # media(6, 10)
    extra = race.game.sessions[-1]
    assert extra.included and race.vote(a_slot) == 6.0                 # il voto ordinario non cambia
    assert race.exclude_extra(extra.id)
    assert round_points(race.game, bugio, "A") == pytest.approx(6.0)


def test_live_session_blocks_everything():
    race = make_race()
    slot = slots(race.game.rounds[0])[0]
    race.begin_session(slot, "new")
    assert race.live and race.locked
    assert race.begin_session(slot, "new") is None and not race.add_round() and not race.undo()


def test_closed_program_marks_pending_session_cancelled():
    race = make_race()
    race.begin_session(slots(race.game.rounds[0])[0], "new")
    reloaded = Race.from_dict(race.to_dict())
    assert not reloaded.live and reloaded.game.sessions[-1].status == "cancelled"


# ---------------------------------------------------------------- configurazione: undo, conteggio, sequenze, modelli
def test_undo_restores_previous_state():
    race = make_race()
    before = [r.name for r in race.game.rounds]
    race.delete_round(race.game.rounds[1].id)
    assert len(race.game.rounds) == 3 and race.undo()
    assert [r.name for r in race.game.rounds] == before


def test_text_edits_are_one_undo_step():
    race = make_race()
    rid = race.game.rounds[0].id
    for text in ("B", "Bu", "Bug"):
        race.set_round_text(rid, "name", text)
    assert race.undo() and race.game.rounds[0].name == "Il Bug-io"


def test_empty_round_name_is_not_applied():
    race = make_race()
    rid = race.game.rounds[0].id
    assert not race.set_round_text(rid, "name", "   ") and race.game.rounds[0].name == "Il Bug-io"


def test_duplicate_goes_after_original_without_votes():
    race = make_race()
    original = race.game.rounds[0]
    record(race, original, [7.0, 8.0])
    copy_ = race.duplicate_round(original.id)
    assert race.game.rounds[1] is copy_ and copy_.name == "Il Bug-io · copia"
    assert all(race.vote(s) is None for s in slots(copy_))


def test_move_round_and_turns():
    race = make_race()
    names = [r.name for r in race.game.rounds]
    assert race.move_round(0, 2)
    assert [r.name for r in race.game.rounds] == [names[1], names[2], names[0], names[3]]
    rid = race.game.rounds[0].id
    race.set_order(rid, "alt")
    race.set_count(rid, 2)                                 # A B A B  (la manche spostata e' "Bazze volanti")
    assert race.move_turn(rid, 0, 3)                       # sposta A1 in fondo
    assert race.game.rounds[0].order == "custom" and sequence(race.game.rounds[0]) == ["B", "A", "B", "A"]


def test_count_change_adapts_or_regenerates_custom_sequence():
    race = make_race()
    rnd = race.game.rounds[0]
    race.set_count(rnd.id, 2)
    race.move_turn(rnd.id, 0, 3)                          # B A B A
    assert race.count_impact(rnd.id, 3) == (0, True)
    race.set_count(rnd.id, 3, "adapt")
    assert sequence(rnd)[:4] == ["B", "A", "B", "A"] and len(sequence(rnd)) == 6
    race.set_count(rnd.id, 1, "regenerate")
    assert sequence(rnd) == ["A", "B"]


def test_reducing_count_removes_votes_from_board():
    race = make_race()
    rnd = race.game.rounds[0]
    race.set_count(rnd.id, 2)
    record(race, rnd, [6, 7, 8, 9])
    assert race.count_impact(rnd.id, 1)[0] == 2
    race.set_count(rnd.id, 1)
    assert sorted(k for k in race.game.votes) == sorted(s.key for s in slots(rnd))


def test_model_catalog_rules():
    race = make_race()
    assert race.model_name_error("") and race.model_name_error("gara di bugie")        # vuoto / gia' esistente
    assert race.save_model("Mio modello", "descr") == ""
    assert race.game.source == race.custom_models[0].id and race.can_update_model
    race.set_round_text(race.game.rounds[0].id, "name", "Cambiato")
    assert race.update_model() and race.custom_models[0].rounds[0].name == "Cambiato"
    assert race.delete_model(race.custom_models[0].id) and race.game.source is None
    assert not race.delete_model("builtin")                                            # i predefiniti non si eliminano


def test_builtin_cannot_be_updated():
    race = make_race()
    assert race.game.source == "builtin" and not race.can_update_model and not race.update_model()


def test_loading_model_replaces_rounds_keeps_names_and_drops_votes():
    race = make_race()
    race.set_name("A", "Anna")
    record(race, race.game.rounds[0], [7.0, 8.0])
    race.save_model("M", "")
    assert race.load_model("builtin")
    assert race.game.names["A"] == "Anna" and not race.game.votes and race.game.source == "builtin"


def test_deactivated_round_is_ignored_by_board():
    race = make_race()
    race.set_active(race.game.rounds[3].id, False)
    board = race.board()
    assert board.active == 3
    assert race.begin_session(slots(race.game.rounds[3])[0], "new") is None
