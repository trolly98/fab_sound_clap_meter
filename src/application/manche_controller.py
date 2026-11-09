from PySide6.QtCore import Property, QObject, Signal, Slot

from infrastructure.json_race_store import JsonRaceStore
from manche.presenter import UiSelection, current_round, current_slot, present
from manche.race import Race
from manche.sequence import slots

from .applause_analyzer_controller import ApplauseAnalyzerController


class MancheController(QObject):
    """Collega la gara (regole) alla grafica e all'analizzatore. Nessuna regola di gara qui: solo coordinamento."""

    changed = Signal()
    notice = Signal(str)           # messaggi brevi per l'operatore
    pageRequested = Signal(str)    # "run" | "board" | "config"

    def __init__(self, race: Race, store: JsonRaceStore, applause: ApplauseAnalyzerController, parent=None):
        super().__init__(parent)
        self._race, self._store, self._applause = race, store, applause
        self._sel = UiSelection()
        self._applause.sessionFinished.connect(self._on_session_finished)
        self._select(race.next_slot())
        self._view = present(race, self._sel)

    # ------------------------------------------------------------ infrastruttura
    def _refresh(self) -> None:
        if self._race.round_by_id(self._sel.round_id) is None:
            self._sel.round_id = self._sel.slot_key = None
        if not any(r.id == self._sel.config_id for r in self._race.game.rounds):
            self._sel.config_id = None
        self._view = present(self._race, self._sel)
        self.changed.emit()

    def _commit(self, message: str = "") -> None:
        self._store.save(self._race.to_dict())
        self._refresh()
        if message:
            self.notice.emit(message)

    def _select(self, slot) -> None:
        if slot:
            self._sel.round_id, self._sel.slot_key = slot.round_id, slot.key

    @Slot()
    def save(self) -> None:
        self._store.save(self._race.to_dict())

    view = Property("QVariantMap", lambda s: s._view, notify=changed)

    # ------------------------------------------------------------ misura (conduzione)
    @Slot(str)
    def selectRound(self, round_id: str) -> None:
        if not self._race.live:
            self._sel.round_id, self._sel.slot_key = round_id, None
            self._refresh()

    @Slot(str)
    def selectSlot(self, key: str) -> None:
        if not self._race.live:
            self._sel.slot_key = key
            self._refresh()

    @Slot()
    def nextTurn(self) -> None:
        self._select(self._race.next_slot())
        self._refresh()

    @Slot(str, bool, result=bool)
    def startMeasurement(self, mode: str, auto: bool) -> bool:
        """mode: new | replace | extra.  auto=True: la sessione si ferma da sola dopo la durata impostata."""
        rnd = current_round(self._race, self._sel)
        if rnd is None:
            return False
        slot = current_slot(self._race, self._sel, rnd)
        session = self._race.begin_session(slot, mode, auto)
        if session is None:
            return False
        self._select(slot)
        self._applause.begin(session.id, self._applause.session_duration_s if auto else None)
        self._commit()
        return True

    @Slot()
    def stopMeasurement(self) -> None:
        self._applause.stop()

    @Slot()
    def cancelMeasurement(self) -> None:
        self._applause.cancel()

    def _on_session_finished(self, token: str, status: str, final_score: float, _elapsed: float) -> None:
        active = self._race.game.active_session
        if active is None or active.id != token:        # solo la sessione che abbiamo avviato noi, mai un altro stop
            return
        value = final_score if status == "valid" else None
        message = self._race.finish_session(status, value)
        self._commit(message)

    @Slot(str)
    def excludeExtra(self, session_id: str) -> None:
        if self._race.exclude_extra(session_id):
            self._commit("Media aggiornata.")

    # ------------------------------------------------------------ proclamazione e spareggio
    @Slot()
    def announce(self) -> None:
        if self._race.announce():
            self._commit("Risultato proclamato.")

    @Slot()
    def reopen(self) -> None:
        if self._race.reopen():
            self._commit("Gara riaperta.")

    @Slot()
    def startTie(self) -> None:
        tie = self._race.start_tie()
        if tie:
            self._select(slots(tie)[0])
            self._commit("Spareggio pronto.")
            self.pageRequested.emit("run")

    @Slot()
    def gotoTie(self) -> None:
        board = self._race.board()
        self._select(self._race.next_slot() or (slots(board.tie_round)[0] if board.tie_round else None))
        self._refresh()
        self.pageRequested.emit("run")

    # ------------------------------------------------------------ configurazione
    @Slot(str, str)
    def setPersonName(self, person: str, text: str) -> None:
        if self._race.set_name(person, text):
            self._commit()

    @Slot(str)
    def selectConfigRound(self, round_id: str) -> None:
        self._sel.config_id = round_id or None
        self._race.end_text_group()
        self._refresh()

    @Slot()
    def addRound(self) -> None:
        created = self._race.add_round()
        if created:
            self._sel.config_id = created.id
            self._commit("Manche aggiunta.")

    @Slot(str)
    def duplicateRound(self, round_id: str) -> None:
        created = self._race.duplicate_round(round_id)
        if created:
            self._sel.config_id = created.id
            self._commit("Manche duplicata.")

    @Slot(str)
    def deleteRound(self, round_id: str) -> None:
        if self._race.delete_round(round_id):
            self._sel.config_id = None
            self._commit("Manche eliminata.")

    @Slot(int, int)
    def moveRound(self, source: int, target: int) -> None:
        if self._race.move_round(source, target):
            self._commit("Ordine delle manche aggiornato.")

    @Slot(str, bool)
    def setRoundActive(self, round_id: str, active: bool) -> None:
        if self._race.set_active(round_id, active):
            self._commit("Attivazione aggiornata.")

    @Slot(str, str, str)
    def setRoundText(self, round_id: str, field_name: str, value: str) -> None:
        if self._race.set_round_text(round_id, field_name, value):
            self._commit()

    @Slot(str, str)
    def setRoundOrder(self, round_id: str, order: str) -> None:
        if self._race.set_order(round_id, order):
            self._commit("Sequenza aggiornata.")

    @Slot(str, str)
    def setRoundMethod(self, round_id: str, method: str) -> None:
        if self._race.set_method(round_id, method):
            self._commit("Regola di punteggio aggiornata.")

    @Slot(str, int, result="QVariantMap")
    def previewCount(self, round_id: str, count: int) -> dict:
        removed, needs_choice = self._race.count_impact(round_id, count)
        return {"removed": removed, "needsChoice": needs_choice}

    @Slot(str, int, str)
    def setRoundCount(self, round_id: str, count: int, sequence_mode: str) -> None:
        if self._race.set_count(round_id, count, sequence_mode or "adapt"):
            self._commit("Regola di punteggio aggiornata.")

    @Slot(str, int, int)
    def moveTurn(self, round_id: str, source: int, target: int) -> None:
        if self._race.move_turn(round_id, source, target):
            self._commit("Sequenza personalizzata aggiornata.")

    # ------------------------------------------------------------ modelli, nuova gara, annulla
    @Slot(str, result=str)
    def validateModelName(self, name: str) -> str:
        return self._race.model_name_error(name)

    @Slot(str, str, result=str)
    def saveModel(self, name: str, description: str) -> str:
        error = self._race.save_model(name, description)
        if not error:
            self._commit("Modello salvato.")
        return error

    @Slot()
    def updateModel(self) -> None:
        if self._race.update_model():
            self._commit("Modello aggiornato.")

    @Slot(str)
    def deleteModel(self, model_id: str) -> None:
        if self._race.delete_model(model_id):
            self._commit("Modello eliminato.")

    @Slot(str)
    def loadModel(self, model_id: str) -> None:
        if self._race.load_model(model_id):
            self._after_new_game("Nuova gara pronta.")

    @Slot(str)
    def newGame(self, kind: str) -> None:
        if self._race.new_game(kind):
            self._after_new_game("Nuova gara pronta.")

    def _after_new_game(self, message: str) -> None:
        self._sel = UiSelection()
        self._select(self._race.next_slot())
        self._commit(message)

    @Slot()
    def undo(self) -> None:
        if self._race.undo():
            self._sel.config_id = None
            self._select(self._race.next_slot())
            self._commit("Ultima modifica annullata.")
