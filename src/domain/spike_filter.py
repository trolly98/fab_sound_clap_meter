from collections import deque
from statistics import median


class SpikeFilter:
    """Toglie i picchi brevi di volume (colpi, urla, battiti isolati) e lascia passare gli applausi.

    Per ogni campione si confronta il livello con la base (mediana degli ultimi campioni *puliti*).
    Un campione sopra `base + soglia` apre un "gruppo": il gruppo comprende i campioni successivi che restano
    sopra `base + soglia/2` (cosi' si prende anche la coda di decadimento) e si chiude dopo `quiet_samples`
    campioni calmi. Guardando in avanti si decide:
      - gruppo breve (al massimo `max_spike_samples`) e poi calma  -> SPIKE: sostituito con la base;
      - gruppo lungo o che continua (applauso)                    -> passa intatto.
    Gli spike vicini (< quiet_samples) si fondono in un unico gruppo: un doppio colpo e' un solo spike, mentre
    battiti ravvicinati di un applauso diventano un gruppo lungo e passano.
    Costo: la misura e' in ritardo di `delay_samples` campioni.
    """

    def __init__(self, max_spike_samples: int, quiet_samples: int, threshold_db: float, baseline_samples: int = 10):
        self._max = max_spike_samples
        self._quiet = quiet_samples
        self._threshold_db = threshold_db
        self._lookahead = max_spike_samples + quiet_samples
        self._pending: deque[float] = deque()
        self._history: deque[float] = deque(maxlen=baseline_samples)
        self._suppress_left = 0
        self._in_signal = False
        self._quiet_run = 0

    @property
    def delay_samples(self) -> int:
        return self._lookahead

    def filter(self, db: float) -> float:
        self._pending.append(db)
        if len(self._pending) <= self._lookahead:
            return self._pending[0]          # avvio: tiene il primo valore finche' non vede abbastanza futuro
        sample = self._pending.popleft()
        out = self._decide(sample, list(self._pending))
        self._history.append(out)
        return out

    def _decide(self, sample: float, future: list[float]) -> float:
        baseline = median(self._history) if self._history else sample
        trigger, release = baseline + self._threshold_db, baseline + self._threshold_db / 2
        if self._suppress_left > 0:
            self._suppress_left -= 1
            return baseline
        if self._in_signal:
            self._follow_signal(sample, release)
            return sample
        if sample <= trigger:
            return sample
        last_member = self._last_member_of_spike(release, future)
        if last_member is None:
            self._in_signal, self._quiet_run = True, 0
            return sample
        self._suppress_left = last_member
        return baseline

    def _follow_signal(self, sample: float, release: float) -> None:
        self._quiet_run = self._quiet_run + 1 if sample <= release else 0
        if self._quiet_run >= self._quiet:
            self._in_signal = False

    def _last_member_of_spike(self, release: float, future: list[float]) -> int | None:
        """Indice dell'ultimo campione del gruppo, oppure None se non e' uno spike."""
        last = 0
        for index, value in enumerate(future, start=1):
            if value > release:
                if index - last - 1 >= self._quiet:
                    break
                last = index
        too_long = last + 1 > self._max
        not_settled = len(future) - last < self._quiet
        return None if too_long or not_settled else last
