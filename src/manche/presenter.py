"""Trasforma lo stato della gara in dati semplici (dizionari e liste) pronti per la grafica, con i testi in italiano."""
from __future__ import annotations

import time
from dataclasses import dataclass

from .entities import METHODS, ORDERS, PEOPLE, Round, Session, Slot
from .race import BAZZE, Race
from .scoring import Scoreboard, extra_sessions, hundredth, personal_votes, round_points
from .sequence import sequence, slots


@dataclass
class UiSelection:
    config_id: str | None = None      # manche aperta nella configurazione
    round_id: str | None = None       # manche selezionata nella conduzione
    slot_key: str | None = None       # turno selezionato nella conduzione


def fmt(value: float | None) -> str:
    return "—" if value is None else f"{hundredth(value):.2f}".replace(".", ",")


def person_name(race: Race, person: str) -> str:
    return race.game.names.get(person, "").strip() or f"Concorrente {person}"


# ------------------------------------------------------------------ selezione corrente
def current_round(race: Race, sel: UiSelection) -> Round | None:
    return (race.round_by_id(sel.round_id)
            or (race.game.tie_rounds[-1] if race.game.tie_rounds else None)
            or next((r for r in race.game.rounds if r.active), None)
            or (race.game.rounds[0] if race.game.rounds else None))


def current_slot(race: Race, sel: UiSelection, rnd: Round) -> Slot:
    options = slots(rnd)
    return (next((s for s in options if s.key == sel.slot_key), None)
            or next((s for s in options if race.vote(s) is None), None) or options[-1])


def last_session(race: Race, key: str) -> Session | None:
    return next((s for s in reversed(race.game.sessions) if s.key == key), None)


# ------------------------------------------------------------------ testi
def method_label(race: Race, rnd: Round) -> str:
    extras = any(extra_sessions(race.game, rnd, p) for p in PEOPLE)
    return "Media con misure straordinarie" if extras else METHODS[rnd.method]


def round_label(race: Race, rnd: Round) -> str:
    if not rnd.active:
        return "Disattivata"
    return "1 voto per sfidante" if rnd.count == 1 else f"{rnd.count} voti · {method_label(race, rnd)}"


def recorded(race: Race, rnd: Round) -> int:
    return sum(race.vote(s) is not None for s in slots(rnd))


# ------------------------------------------------------------------ parti
def present_header(race: Race, board: Scoreboard) -> dict:
    game = race.game
    if game.result:
        status = "Risultato proclamato"
    elif board.tie_round:
        status = "Spareggio"
    elif board.ready:
        status = "Pronto per la proclamazione" if board.lead else "Parità da risolvere"
    else:
        status = "Gara in corso" if game.votes or race.live else "In attesa di misure"
    return {
        "modelName": race.source_model.name if race.source_model else "Gara senza modello", "status": status,
        "totalsLabel": "Totale finale" if board.ready else "Totale progressivo",
        "totals": {p: fmt(board.total[p]) for p in PEOPLE}, "names": {p: person_name(race, p) for p in PEOPLE},
        "done": board.done, "active": board.active, "progress": 100 * board.done / board.active if board.active else 0,
    }


def present_config(race: Race, sel: UiSelection) -> dict:
    rounds = race.game.rounds
    chosen = next((r for r in rounds if r.id == sel.config_id), None)
    selected = None
    if chosen:
        selected = {
            "id": chosen.id, "name": chosen.name, "notes": chosen.notes, "count": chosen.count, "method": chosen.method,
            "order": chosen.order, "active": chosen.active, "rulesLocked": chosen.kind == BAZZE,
            "turns": [{"index": i, "label": s.label, "person": s.person, "personName": person_name(race, s.person),
                       "position": s.order} for i, s in enumerate(slots(chosen))],
        }
    return {
        "rounds": [{"id": r.id, "name": r.name, "active": r.active, "selected": r.id == sel.config_id,
                    "canUp": i > 0, "canDown": i < len(rounds) - 1} for i, r in enumerate(rounds)],
        "selected": selected,
        "orders": [{"id": k, "label": v} for k, v in ORDERS.items()],
        "methods": [{"id": k, "label": v} for k, v in METHODS.items()],
        "counts": list(range(1, 21)),
    }


def present_cards(race: Race, rnd: Round) -> list[dict]:
    cards = []
    for person in PEOPLE:
        chips = [{"text": fmt(v), "extra": False, "sessionId": ""} for v in personal_votes(race.game, rnd, person)]
        chips += [{"text": f"+ {fmt(s.value)}", "extra": True, "sessionId": s.id} for s in extra_sessions(race.game, rnd, person)]
        cards.append({"person": person, "name": person_name(race, person),
                      "points": fmt(round_points(race.game, rnd, person)), "votes": chips})
    return cards


def present_run(race: Race, sel: UiSelection) -> dict:
    rnd = current_round(race, sel)
    if rnd is None:
        return {"hasRound": False}
    slot = current_slot(race, sel, rnd)
    active = race.game.active_session
    measuring_key = active.key if active else None
    entries = [{"id": r.id, "number": f"{i + 1:02d}", "name": r.name, "label": round_label(race, r), "tie": r.kind == "tie",
                "recorded": recorded(race, r), "count": len(slots(r)), "active": r.active, "selected": r.id == rnd.id}
               for i, r in enumerate(race.entries())]
    turn_slots = []
    for s in slots(rnd):
        saved, last = race.vote(s), last_session(race, s.key)
        status = ("● In corso" if s.key == measuring_key else f"✓ {fmt(saved)}" if saved is not None
                  else "Vuota" if last and last.status == "empty" else "Annullata" if last and last.status == "cancelled"
                  else "Da misurare")
        turn_slots.append({"key": s.key, "label": s.label, "person": s.person, "personName": person_name(race, s.person),
                           "turn": f"Turno {s.order}", "status": status, "selected": s.key == slot.key,
                           "measuring": s.key == measuring_key})
    saved, last = race.vote(slot), last_session(race, slot.key)
    measuring = slot.key == measuring_key
    outcome = ("Misura in corso" if measuring else "Ultima misura annullata" if last and last.status == "cancelled"
               else "Ultima misura vuota" if last and last.status == "empty"
               else "Voto definitivo registrato" if saved is not None else "Pronto per la misura")
    blocked = race.locked or not rnd.active
    return {
        "hasRound": True, "entries": entries,
        "round": {"name": rnd.name, "notes": rnd.notes, "tie": rnd.kind == "tie", "label": round_label(race, rnd),
                  "eyebrow": "Spareggio" if rnd.kind == "tie" else "Manche selezionata"},
        "slots": turn_slots,
        "slot": {"key": slot.key, "label": slot.label, "person": slot.person, "personName": person_name(race, slot.person),
                 "hasVote": saved is not None, "voteText": fmt(saved), "measuring": measuring, "outcome": outcome,
                 "outcomeTone": "good" if measuring else "warn" if last and last.status != "valid" and saved is None else "",
                 "canStart": not blocked and saved is None, "canCorrect": not blocked and saved is not None,
                 "roundName": rnd.name},
        "cards": present_cards(race, rnd),
        "nextTurn": (lambda n: n.key if n else "")(race.next_slot()),
        "canNext": not race.locked and race.next_slot() is not None and race.next_slot().key != slot.key,
        "hasHistory": bool(race.game.sessions),
    }


def _result_card(race: Race, board: Scoreboard) -> dict:
    result = race.game.result
    live = race.live
    card = {"title": "Risultato in attesa",
            "body": "Completa i voti richiesti nelle manche attive per sbloccare la proclamazione.", "actions": []}
    totals = f"Totali di gara · {person_name(race, 'A')} {fmt(board.total['A'])} · {person_name(race, 'B')} {fmt(board.total['B'])}"
    if result:
        card["title"] = (f"{person_name(race, result.winner)} vince" + (" allo spareggio" if result.via == "spareggio" else "")
                         if result.winner else "Pareggio proclamato")
        card["body"] = totals
        card["actions"] = [{"id": "reopen", "label": "Riapri gara…", "primary": False, "enabled": True}]
    elif board.ready:
        lead = board.lead or board.tie_lead
        if lead:
            card["title"] = f"{person_name(race, 'A' if lead > 0 else 'B')} in testa"
            card["body"] = "Spareggio completo. Puoi proclamare il vincitore." if board.tie_lead else "Tutte le manche attive sono complete."
            card["actions"] = [{"id": "announce", "label": "Proclama vincitore", "primary": True, "enabled": not live}]
        elif board.tie_pending:
            card["title"] = "Spareggio da completare"
            card["body"] = "Registra un voto per ciascuno sfidante. I totali della gara restano separati."
            card["actions"] = [{"id": "goto-tie", "label": "Vai allo spareggio", "primary": True, "enabled": True}]
        else:
            card["title"] = "Parità allo spareggio" if board.tie_round else "Pareggio finale"
            card["body"] = "Puoi confermare il pareggio o decidere la gara con uno spareggio."
            card["actions"] = [
                {"id": "announce", "label": "Conferma pareggio", "primary": False, "enabled": not live},
                {"id": "tie", "label": "Nuovo spareggio" if board.tie_round else "Avvia spareggio", "primary": True, "enabled": not live}]
    return card


def present_board(race: Race, board: Scoreboard) -> dict:
    rows = []
    for line in board.lines:
        row = {"name": line.round.name, "label": round_label(race, line.round), "active": line.round.active}
        for person in PEOPLE:
            row[person] = {"votes": " · ".join(fmt(v) for v in personal_votes(race.game, line.round, person)),
                           "points": fmt(line.points[person]), "total": fmt(line.total[person])}
        rows.append(row)
    return {
        "result": _result_card(race, board), "rows": rows,
        "totalLabel": "Totale finale" if board.ready else "Totale progressivo",
        "totals": {p: fmt(board.total[p]) for p in PEOPLE}, "names": {p: person_name(race, p) for p in PEOPLE},
        "ties": [{"name": t.name, "cards": present_cards(race, t)} for t in race.game.tie_rounds],
        "hasHistory": bool(race.game.sessions),
    }


def present_history(race: Race) -> list[dict]:
    status = {"valid": "Valida", "empty": "Vuota", "cancelled": "Annullata"}
    modes = {"new": "Ordinaria", "replace": "Sostitutiva", "extra": "Aggiuntiva"}
    return [{"round": s.round_name, "turn": f"{s.person}{s.index}", "person": person_name(race, s.person),
             "status": status.get(s.status, s.status), "mode": modes.get(s.mode, s.mode) + (" · automatica" if s.auto else ""),
             "value": fmt(s.value), "time": time.strftime("%H:%M:%S", time.localtime(s.ended or s.started)),
             "reason": s.reason, "included": s.included}
            for s in reversed(race.game.sessions)]


def present_models(race: Race) -> list[dict]:
    return [{"id": m.id, "name": m.name, "description": m.description, "custom": m.id != "builtin",
             "category": "Personalizzato" if m.id != "builtin" else "Predefinito",
             "preview": " · ".join(f"{r.name} ({r.count})" for r in m.rounds) or "Nessuna manche",
             "current": m.id == race.game.source} for m in race.models()]


def present(race: Race, sel: UiSelection) -> dict:
    board = race.board()
    model = race.source_model
    return {
        "live": race.live, "locked": race.locked, "canUndo": race.can_undo, "hasResult": race.game.result is not None,
        "lockReason": "Configurazione sospesa durante la misura." if race.live
                      else "Riapri la gara dalla conduzione per modificare la configurazione." if race.game.result else "",
        "names": dict(race.game.names), "header": present_header(race, board),
        "model": {"name": model.name if model else "Senza modello", "exists": model is not None,
                  "category": "" if not model else "Predefinito" if model.id == "builtin" else "Personalizzato",
                  "canUpdate": race.can_update_model, "canSave": not race.locked and bool(race.game.rounds)},
        "config": present_config(race, sel), "run": present_run(race, sel), "board": present_board(race, board),
        "history": present_history(race), "models": present_models(race),
    }
