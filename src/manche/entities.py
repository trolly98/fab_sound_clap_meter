from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields

PEOPLE = ("A", "B")
METHODS = {"mean": "Media aritmetica", "sum": "Somma", "max": "Voto più alto", "last": "Ultimo voto"}
ORDERS = {"alt": "Alternata", "consecutive": "Consecutiva", "reverse": "Invertita al secondo giro", "custom": "Personalizzata"}


def _pick(cls, data: dict) -> dict:
    return {f.name: data[f.name] for f in fields(cls) if f.name in data}


@dataclass
class Round:
    id: str
    name: str
    notes: str = ""
    count: int = 1                       # misurazioni ordinarie per sfidante
    order: str = "alt"                   # alt | consecutive | reverse | custom
    kind: str = "custom"                 # custom | bugio | bazze | tribunale | balla | tie
    method: str = "mean"                 # mean | sum | max | last
    custom: list[str] = field(default_factory=list)
    active: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "Round":
        return cls(**_pick(cls, data))


@dataclass(frozen=True)
class Slot:
    """Un turno di intervento: il voto di `person` numero `index` in una manche."""

    round_id: str
    person: str
    index: int       # A1, A2... (ordine di apparizione dello sfidante)
    order: int       # posizione nella sequenza della manche (1, 2, 3...)

    @property
    def key(self) -> str:
        return f"{self.round_id}:{self.person}:{self.index}"

    @property
    def label(self) -> str:
        return f"{self.person}{self.index}"


@dataclass
class Vote:
    value: float
    session_id: str


@dataclass
class Session:
    """Una sessione di ascolto: esito esplicito, legata a gara, manche, turno e sfidante."""

    id: str
    game_id: str
    round_id: str
    round_name: str
    person: str
    index: int
    order: int
    key: str
    mode: str                            # new | replace | extra
    started: float
    status: str = "active"               # active | valid | empty | cancelled
    value: float | None = None
    included: bool = False               # solo per le misure straordinarie: entra nella media
    ended: float | None = None
    auto: bool = False                   # avviata come sessione automatica
    reason: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(**_pick(cls, data))


@dataclass
class Result:
    winner: str | None                   # "A", "B" oppure None (pareggio)
    via: str                             # gara | spareggio
    at: float


@dataclass
class Game:
    id: str
    source: str | None
    names: dict[str, str]
    rounds: list[Round]
    votes: dict[str, Vote] = field(default_factory=dict)
    sessions: list[Session] = field(default_factory=list)
    tie_rounds: list[Round] = field(default_factory=list)
    result: Result | None = None
    active_session: Session | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        return cls(
            id=data["id"], source=data.get("source"), names=dict(data.get("names", {})),
            rounds=[Round.from_dict(r) for r in data.get("rounds", [])],
            votes={k: Vote(**v) for k, v in data.get("votes", {}).items()},
            sessions=[Session.from_dict(s) for s in data.get("sessions", [])],
            tie_rounds=[Round.from_dict(r) for r in data.get("tie_rounds", [])],
            result=Result(**data["result"]) if data.get("result") else None,
            active_session=Session.from_dict(data["active_session"]) if data.get("active_session") else None,
        )


@dataclass
class RaceModel:
    id: str
    name: str
    description: str
    rounds: list[Round]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RaceModel":
        return cls(data["id"], data["name"], data.get("description", ""), [Round.from_dict(r) for r in data["rounds"]])
