from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.entities.base import AggregateRoot
from app.domain.exceptions.equipment import ArtifactAlreadyEquippedError


@dataclass
class EquippedArtifact:
    item_id: UUID
    bonuses: dict


@dataclass
class Equipment(AggregateRoot):
    ship_id: UUID
    id: UUID = field(default_factory=uuid4)
    artifacts: list[EquippedArtifact | None] = field(default_factory=list)

    def equip(self, item_id: UUID, bonuses: dict, slot_index: int, max_slots: int) -> EquippedArtifact | None:
        if slot_index < 0 or slot_index >= max_slots:
            raise ValueError(
                f"Invalid slot index {slot_index}. Must be 0-{max_slots - 1}"
            )

        if any(a is not None and a.item_id == item_id for a in self.artifacts):
            raise ArtifactAlreadyEquippedError(item_id)

        while len(self.artifacts) <= slot_index:
            self.artifacts.append(None)

        replaced = self.artifacts[slot_index]
        self.artifacts[slot_index] = EquippedArtifact(item_id=item_id, bonuses=bonuses)
        return replaced

    def unequip(self, item_id: UUID) -> EquippedArtifact:
        idx = next(
            (i for i, a in enumerate(self.artifacts) if a is not None and a.item_id == item_id),
            None,
        )
        if idx is None:
            raise ValueError(f"Artifact {item_id} is not equipped")

        removed = self.artifacts[idx]
        self.artifacts[idx] = None
        return removed

    def get_total_bonuses(self) -> dict:
        total: dict[str, float] = {}
        for artifact in self.artifacts:
            if artifact is None:
                continue
            for key, value in artifact.bonuses.items():
                total[key] = total.get(key, 0) + value
        return total
