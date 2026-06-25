from dataclasses import dataclass


@dataclass(frozen=True)
class TeaLevel:
    value: float

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Tea level cannot be negative")

    def consume(self, amount: float) -> "TeaLevel":
        return TeaLevel(max(0.0, self.value - amount))

    def restore(self, amount: float, max_level: float = 100.0) -> "TeaLevel":
        return TeaLevel(min(self.value + amount, max_level))


@dataclass(frozen=True)
class Optimism:
    value: float

    def __post_init__(self):
        if self.value < 0 or self.value > 100:
            raise ValueError("Optimism must be between 0 and 100")

    def apply_damage(self, risk: float, defense: float) -> "Optimism":
        damage = max(0.0, risk - defense)
        new_value = max(0.0, self.value - damage)
        return Optimism(new_value)

    def restore(self, amount: float) -> "Optimism":
        return Optimism(min(self.value + amount, 100.0))

    def is_destroyed(self) -> bool:
        return self.value <= 0


@dataclass(frozen=True)
class XgenBalance:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("XGen balance cannot be negative")

    def add(self, amount: int) -> "XgenBalance":
        return XgenBalance(self.value + amount)

    def spend(self, amount: int) -> "XgenBalance":
        if self.value < amount:
            from app.domain.exceptions.player import InsufficientXgenError
            raise InsufficientXgenError(required=amount, available=self.value)
        return XgenBalance(self.value - amount)


@dataclass(frozen=True)
class FragmentsBalance:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Fragments balance cannot be negative")

    def add(self, amount: int) -> "FragmentsBalance":
        return FragmentsBalance(self.value + amount)

    def spend(self, amount: int) -> "FragmentsBalance":
        if self.value < amount:
            from app.domain.exceptions.player import InsufficientFragmentsError
            raise InsufficientFragmentsError(required=amount, available=self.value)
        return FragmentsBalance(self.value - amount)
