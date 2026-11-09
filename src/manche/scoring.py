import math
from dataclasses import dataclass

from .entities import PEOPLE, Game, Round, Session
from .sequence import slots


def hundredth(value: float) -> float:
    """Arrotonda a due decimali (mezzo verso l'alto): e' la precisione dei voti e dei confronti."""
    return math.floor(value * 100 + 0.5 + 1e-9) / 100


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def vote_value(game: Game, key: str) -> float | None:
    vote = game.votes.get(key)
    return vote.value if vote else None


def personal_votes(game: Game, rnd: Round, person: str) -> list[float | None]:
    return [vote_value(game, s.key) for s in slots(rnd) if s.person == person]


def extra_sessions(game: Game, rnd: Round, person: str) -> list[Session]:
    return [s for s in game.sessions
            if s.round_id == rnd.id and s.person == person and s.mode == "extra" and s.status == "valid" and s.included]


def round_points(game: Game, rnd: Round, person: str) -> float | None:
    """Punteggio valido della manche per uno sfidante; None finche' mancano voti ordinari."""
    values = personal_votes(game, rnd, person)
    if not rnd.active or any(v is None for v in values):
        return None
    extras = extra_sessions(game, rnd, person)
    if extras:
        return mean([*values, *(s.value for s in extras)])
    return {"mean": mean(values), "sum": sum(values), "max": max(values), "last": values[-1]}[rnd.method]


@dataclass
class BoardLine:
    round: Round
    points: dict[str, float | None]
    total: dict[str, float | None]       # progressivo dopo questa manche
    complete: bool


@dataclass
class Scoreboard:
    total: dict[str, float | None]
    lines: list[BoardLine]
    active: int
    done: int
    ready: bool
    lead: float                          # A meno B, ai centesimi
    tie_round: Round | None
    tie_ready: bool
    tie_lead: float

    @property
    def tie_pending(self) -> bool:
        return self.tie_round is not None and not self.tie_ready


def scoreboard(game: Game) -> Scoreboard:
    total: dict[str, float | None] = {person: None for person in PEOPLE}
    lines = []
    for rnd in game.rounds:
        points = {person: round_points(game, rnd, person) for person in PEOPLE}
        for person in PEOPLE:
            if points[person] is not None:
                total[person] = (total[person] or 0) + points[person]
        lines.append(BoardLine(rnd, points, dict(total), all(points[p] is not None for p in PEOPLE)))
    active = [line for line in lines if line.round.active]
    done = sum(line.complete for line in active)
    lead = hundredth(hundredth(total["A"] or 0) - hundredth(total["B"] or 0))
    tie_round = game.tie_rounds[-1] if game.tie_rounds else None
    tie_points = {p: round_points(game, tie_round, p) for p in PEOPLE} if tie_round else {}
    tie_ready = bool(tie_round) and all(tie_points[p] is not None for p in PEOPLE)
    tie_lead = hundredth(hundredth(tie_points["A"]) - hundredth(tie_points["B"])) if tie_ready else 0.0
    return Scoreboard(total, lines, len(active), done, bool(active) and done == len(active), lead,
                      tie_round, tie_ready, tie_lead)
