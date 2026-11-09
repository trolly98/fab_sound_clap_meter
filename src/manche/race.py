from __future__ import annotations

import copy
import time
import uuid
from dataclasses import replace
from typing import Callable

from .entities import PEOPLE, Game, Result, RaceModel, Round, Session, Slot, Vote
from .scoring import Scoreboard, scoreboard, vote_value
from .sequence import move_item, sequence, slots

DEFAULT_NAMES = {"A": "Concorrente A", "B": "Concorrente B"}
BUILTIN_ID = "builtin"
BAZZE = "bazze"


def default_id() -> str:
    return uuid.uuid4().hex[:12]


class Race:
    """La gara corrente e il catalogo dei modelli: tutte le regole stanno qui, senza Qt e senza grafica.

    Le modifiche di configurazione sono annullabili (undo) e bloccate durante una misura o dopo la proclamazione.
    """

    HISTORY_LIMIT = 60

    def __init__(self, game: Game | None = None, custom_models: list[RaceModel] | None = None,
                 new_id: Callable[[], str] = default_id, now: Callable[[], float] = time.time):
        self._new_id, self._now = new_id, now
        self.builtin = self._builtin_model()
        self.custom_models: list[RaceModel] = custom_models or []
        self.game = game or self._fresh_game(self.builtin, dict(DEFAULT_NAMES))
        self._history: list[dict] = []
        self._text_group: str | None = None

    # ------------------------------------------------------------------ modelli
    def _builtin_model(self) -> RaceModel:
        def rnd(name, notes, count, order, kind):
            return Round(self._new_id(), name, notes, count, order, kind)
        return RaceModel(BUILTIN_ID, "Gara di Bugie", "Le quattro manche dello spettacolo.", [
            rnd("Il Bug-io", "Bugia di presentazione raccontata in prima persona. Monologo di 5–10 minuti per sfidante.", 1, "alt", "bugio"),
            rnd("Bazze volanti", "Due temi estratti dalla boule. Improvvisazione di massimo 2 minuti per sfidante e per tema.", 2, "reverse", BAZZE),
            rnd("Il Tribunale", "Bugia breve preparata a casa (massimo 2 minuti) e domande dell’avversario.", 1, "alt", "tribunale"),
            rnd("La Grande Balla", "Monologo finale senza vincoli, 5–10 minuti per sfidante.", 1, "alt", "balla"),
        ])

    def models(self) -> list[RaceModel]:
        return [self.builtin, *self.custom_models]

    def model_by_id(self, model_id: str | None) -> RaceModel | None:
        return next((m for m in self.models() if m.id == model_id), None)

    @property
    def source_model(self) -> RaceModel | None:
        return self.model_by_id(self.game.source)

    def _copy_rounds(self, rounds: list[Round]) -> list[Round]:
        return [replace(r, id=self._new_id(), custom=list(r.custom)) for r in rounds]

    def _fresh_game(self, model: RaceModel | None, names: dict[str, str]) -> Game:
        return Game(self._new_id(), model.id if model else None, dict(names), self._copy_rounds(model.rounds) if model else [])

    def model_name_error(self, name: str) -> str:
        name = name.strip()
        if not name:
            return "Inserisci un nome."
        if any(m.name.casefold() == name.casefold() for m in self.models()):
            return "Esiste già un modello con questo nome."
        return ""

    # ------------------------------------------------------------------ stato e interrogazioni
    @property
    def live(self) -> bool:
        return self.game.active_session is not None

    @property
    def locked(self) -> bool:
        return self.live or self.game.result is not None

    def entries(self) -> list[Round]:
        return [*self.game.rounds, *self.game.tie_rounds]

    def round_by_id(self, round_id: str | None) -> Round | None:
        return next((r for r in self.entries() if r.id == round_id), None)

    def vote(self, slot: Slot) -> float | None:
        return vote_value(self.game, slot.key)

    def board(self) -> Scoreboard:
        return scoreboard(self.game)

    def next_slot(self) -> Slot | None:
        pending = self.board().tie_round
        rounds = [pending] if pending else [r for r in self.game.rounds if r.active]
        return next((s for r in rounds for s in slots(r) if self.vote(s) is None), None)

    @property
    def can_undo(self) -> bool:
        return bool(self._history) and not self.locked

    # ------------------------------------------------------------------ salvataggio e annullamento
    def to_dict(self) -> dict:
        return {"game": self.game.to_dict(), "models": [m.to_dict() for m in self.custom_models]}

    def _restore(self, data: dict) -> None:
        self.game = Game.from_dict(data["game"])
        self.custom_models = [RaceModel.from_dict(m) for m in data["models"]]

    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> "Race":
        race = cls(**kwargs)
        race._restore(data)
        stale = race.game.active_session
        if stale:     # il programma e' stato chiuso durante una misura: va registrata come annullata
            race.game.active_session = None
            stale.status, stale.reason, stale.ended = "cancelled", "Programma chiuso durante la misura", race._now()
            race.game.sessions.append(stale)
        return race

    def _snapshot(self) -> None:
        self._history.append(copy.deepcopy(self.to_dict()))
        del self._history[:-self.HISTORY_LIMIT]

    def _edit(self, change: Callable[[], None], text_group: str | None = None) -> bool:
        if self.locked:
            return False
        if text_group is None or text_group != self._text_group:
            self._snapshot()
        self._text_group = text_group
        change()
        return True

    def undo(self) -> bool:
        if not self.can_undo:
            return False
        self._restore(self._history.pop())
        self._text_group = None
        return True

    def end_text_group(self) -> None:
        self._text_group = None

    # ------------------------------------------------------------------ configurazione delle manche
    def set_name(self, person: str, text: str) -> bool:
        return self._edit(lambda: self.game.names.__setitem__(person, text), f"name:{person}")

    def add_round(self) -> Round | None:
        created = Round(self._new_id(), "Nuova manche")
        done = self._edit(lambda: (self.game.rounds.append(created), self.invalidate_tie()))
        return created if done else None

    def duplicate_round(self, round_id: str) -> Round | None:
        original = next((r for r in self.game.rounds if r.id == round_id), None)
        if not original:
            return None
        copy_ = replace(original, id=self._new_id(), name=f"{original.name} · copia", custom=list(original.custom))
        def change():
            self.game.rounds.insert(self.game.rounds.index(original) + 1, copy_)
            self.invalidate_tie()
        return copy_ if self._edit(change) else None

    def delete_round(self, round_id: str) -> bool:
        def change():
            self.game.rounds = [r for r in self.game.rounds if r.id != round_id]
            for key in [k for k in self.game.votes if k.startswith(f"{round_id}:")]:
                del self.game.votes[key]
            self.invalidate_tie()
        return round_id in {r.id for r in self.game.rounds} and self._edit(change)

    def move_round(self, source: int, target: int) -> bool:
        probe = list(self.game.rounds)
        return move_item(probe, source, target) and self._edit(lambda: move_item(self.game.rounds, source, target))

    def set_active(self, round_id: str, active: bool) -> bool:
        rnd = self._config_round(round_id)
        def change():
            rnd.active = active
            self.invalidate_tie()
        return rnd is not None and self._edit(change)

    def set_round_text(self, round_id: str, field_name: str, value: str) -> bool:
        rnd = self._config_round(round_id)
        if rnd is None or field_name not in ("name", "notes"):
            return False
        if field_name == "name" and not value.strip():
            return False               # il nome e' obbligatorio: un campo vuoto non viene applicato
        return self._edit(lambda: setattr(rnd, field_name, value.strip() if field_name == "name" else value),
                          f"{field_name}:{round_id}")

    def set_order(self, round_id: str, order: str) -> bool:
        rnd = self._config_round(round_id)
        def change():
            if order == "custom" and not rnd.custom:
                rnd.custom = sequence(rnd)
            rnd.order = order
        return rnd is not None and self._edit(change)

    def set_method(self, round_id: str, method: str) -> bool:
        rnd = self._config_round(round_id)
        def change():
            rnd.method = method
            self.invalidate_tie()
        return rnd is not None and rnd.kind != BAZZE and self._edit(change)

    def count_impact(self, round_id: str, count: int) -> tuple[int, bool]:
        """(voti che usciranno dal tabellone, serve scegliere come adattare la sequenza personalizzata)."""
        rnd = self._config_round(round_id)
        if rnd is None:
            return 0, False
        removed = sum(1 for s in slots(rnd) if s.index > count and self.vote(s) is not None)
        return removed, rnd.order == "custom"

    def set_count(self, round_id: str, count: int, sequence_mode: str = "adapt") -> bool:
        """sequence_mode: 'adapt' conserva l'ordine personalizzato, 'regenerate' lo rigenera alternato da A."""
        rnd = self._config_round(round_id)
        if rnd is None or rnd.kind == BAZZE or not 1 <= count <= 20:
            return False
        removed = [s for s in slots(rnd) if s.index > count and self.vote(s) is not None]
        def change():
            current = sequence(rnd)
            rnd.count = count
            if rnd.order == "custom":
                rnd.custom = sequence(replace(rnd, order="alt")) if sequence_mode == "regenerate" else sequence(replace(rnd, custom=current))
            for slot in removed:
                self.game.votes.pop(slot.key, None)
            self.invalidate_tie()
        return self._edit(change)

    def move_turn(self, round_id: str, source: int, target: int) -> bool:
        rnd = self._config_round(round_id)
        if rnd is None:
            return False
        order = sequence(rnd)
        if not move_item(order, source, target):
            return False
        def change():
            rnd.custom, rnd.order = order, "custom"
        return self._edit(change)

    def _config_round(self, round_id: str) -> Round | None:
        return next((r for r in self.game.rounds if r.id == round_id), None)

    # ------------------------------------------------------------------ modelli e nuova gara
    def new_game(self, kind: str) -> bool:
        """kind: 'current' (stesse manche), 'builtin' (Gara di Bugie), 'empty' (da zero)."""
        if self.live:
            return False
        model = {"current": RaceModel(self.game.source or "", "", "", self.game.rounds), "builtin": self.builtin, "empty": None}[kind]
        self._snapshot_unconditionally()
        self.game = self._fresh_game(model, self.game.names)
        if kind == "current":
            self.game.source = model.id or None
        return True

    def load_model(self, model_id: str) -> bool:
        model = self.model_by_id(model_id)
        if self.live or model is None:
            return False
        self._snapshot_unconditionally()
        self.game = self._fresh_game(model, self.game.names)
        return True

    def _snapshot_unconditionally(self) -> None:
        self._snapshot()
        self._text_group = None

    def save_model(self, name: str, description: str) -> str:
        """Salva le manche correnti come nuovo modello personalizzato. Restituisce un errore, o '' se riuscito."""
        error = self.model_name_error(name)
        if error or self.locked or not self.game.rounds:
            return error or "Non si può salvare ora."
        saved = RaceModel(self._new_id(), name.strip(), description.strip(), self._copy_rounds(self.game.rounds))
        def change():
            self.custom_models.append(saved)
            self.game.source = saved.id
        self._edit(change)
        return ""

    @property
    def can_update_model(self) -> bool:
        model = self.source_model
        return model is not None and model.id != BUILTIN_ID and not self.locked

    def update_model(self) -> bool:
        model = self.source_model
        if not self.can_update_model:
            return False
        return self._edit(lambda: setattr(model, "rounds", self._copy_rounds(self.game.rounds)))

    def delete_model(self, model_id: str) -> bool:
        model = next((m for m in self.custom_models if m.id == model_id), None)
        if model is None:
            return False
        def change():
            self.custom_models.remove(model)
            if self.game.source == model_id:
                self.game.source = None
        return self._edit(change)

    # ------------------------------------------------------------------ misure
    def begin_session(self, slot: Slot, mode: str, auto: bool = False) -> Session | None:
        rnd = self.round_by_id(slot.round_id)
        if self.locked or rnd is None or not rnd.active:
            return None
        if (mode == "new" and self.vote(slot) is not None) or (mode == "replace" and self.vote(slot) is None):
            return None
        self._history.clear()          # dopo una misura non si torna piu' indietro con Annulla
        session = Session(self._new_id(), self.game.id, rnd.id, rnd.name, slot.person, slot.index, slot.order,
                          slot.key, mode, self._now(), auto=auto)
        self.game.active_session = session
        return session

    def finish_session(self, status: str, value: float | None) -> str:
        """Chiude la sessione attiva con un esito esplicito (valid | empty | cancelled). Restituisce un messaggio."""
        session = self.game.active_session
        if session is None:
            return ""
        self.game.active_session = None
        valid = status == "valid" and value is not None
        session.status = status if valid or status != "valid" else "empty"
        session.ended, session.value = self._now(), value if valid else None
        session.included = valid and session.mode == "extra"
        self.game.sessions.append(session)
        if valid and session.mode != "extra" and (session.mode == "replace" or session.key not in self.game.votes):
            self.game.votes[session.key] = Vote(value, session.id)
        if valid and session.mode != "new" and any(r.id == session.round_id for r in self.game.rounds):
            self.invalidate_tie()
        if session.status == "empty":
            return "Misura vuota (nessun segnale). Puoi riprovare sullo stesso turno."
        if session.status == "cancelled":
            return "Misura annullata. Puoi riprovare sullo stesso turno."
        return "Misura straordinaria inclusa nella media." if session.mode == "extra" else "Voto definitivo registrato."

    def exclude_extra(self, session_id: str) -> bool:
        record = next((s for s in self.game.sessions if s.id == session_id and s.included), None)
        def change():
            record.included = False
            self.invalidate_tie()
        return record is not None and self._edit(change)

    def invalidate_tie(self) -> None:
        for rnd in self.game.tie_rounds:
            for slot in slots(rnd):
                self.game.votes.pop(slot.key, None)
        self.game.tie_rounds = []
        self.game.result = None

    # ------------------------------------------------------------------ proclamazione e spareggio
    def announce(self) -> bool:
        board = self.board()
        if self.locked or not board.ready or board.tie_pending:
            return False
        self._history.clear()
        lead = board.lead or board.tie_lead
        self.game.result = Result("A" if lead > 0 else "B" if lead < 0 else None, "spareggio" if board.tie_lead else "gara", self._now())
        return True

    def reopen(self) -> bool:
        if self.game.result is None:
            return False
        self.game.result = None
        return True

    def start_tie(self) -> Round | None:
        board = self.board()
        if self.locked or not board.ready or board.lead or board.tie_lead or board.tie_pending:
            return None
        self._history.clear()
        tie = Round(self._new_id(), f"Spareggio {len(self.game.tie_rounds) + 1}", kind="tie")
        self.game.tie_rounds.append(tie)
        return tie
