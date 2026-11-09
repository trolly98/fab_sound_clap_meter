from .entities import PEOPLE, Round, Slot


def sequence(rnd: Round) -> list[str]:
    """Ordine degli interventi della manche, es. ['A', 'B', 'B', 'A']."""
    if rnd.order == "consecutive":
        return [person for person in PEOPLE for _ in range(rnd.count)]
    alternate: list[str] = []
    for index in range(rnd.count):
        alternate += ["B", "A"] if rnd.order == "reverse" and index % 2 else list(PEOPLE)
    if rnd.order != "custom":
        return alternate
    left = {person: rnd.count for person in PEOPLE}
    result = []
    for person in [*rnd.custom, *alternate]:       # la parte personalizzata ha la precedenza, il resto completa
        if left[person]:
            left[person] -= 1
            result.append(person)
    return result


def slots(rnd: Round) -> list[Slot]:
    seen = {person: 0 for person in PEOPLE}
    result = []
    for order, person in enumerate(sequence(rnd), start=1):
        seen[person] += 1
        result.append(Slot(rnd.id, person, seen[person], order))
    return result


def move_item(items: list, source: int, target: int) -> bool:
    if source == target or not (0 <= source < len(items)) or not (0 <= target < len(items)):
        return False
    items.insert(target, items.pop(source))
    return True
