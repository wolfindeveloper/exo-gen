from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.entities.base import AggregateRoot
from app.domain.value_objects.equipment import SlotType


@dataclass
class EquippedArtifact:
    item_id: UUID
    slot_type: SlotType
    bonuses: dict


@dataclass
class Equipment(AggregateRoot):
    ship_id: UUID
    id: UUID = field(default_factory=uuid4)
    artifacts: list[EquippedArtifact] = field(default_factory=list)

    def equip(self, item_id: UUID, slot_type: SlotType, bonuses: dict) -> EquippedArtifact | None:
        if any(a.item_id == item_id for a in self.artifacts):
            raise ValueError(f"Artifact {item_id} is already equipped")

        replaced_artifact: EquippedArtifact | None = None
        existing_idx = next(
            (i for i, a in enumerate(self.artifacts) if a.slot_type == slot_type),
            None,
        )
        if existing_idx is not None:
            replaced_artifact = self.artifacts.pop(existing_idx)

        self.artifacts.append(EquippedArtifact(
            item_id=item_id,
            slot_type=slot_type,
            bonuses=bonuses,
        ))
        return replaced_artifact

    def unequip(self, item_id: UUID) -> EquippedArtifact:
        idx = next((i for i, a in enumerate(self.artifacts) if a.item_id == item_id), None)
        if idx is None:
            raise ValueError(f"Artifact {item_id} is not equipped")

        return self.artifacts.pop(idx)

    def get_total_bonuses(self) -> dict:
        seen: dict[SlotType, EquippedArtifact] = {}
        for artifact in self.artifacts:
            seen[artifact.slot_type] = artifact
        total: dict[str, float] = {}
        for artifact in seen.values():
            for key, value in artifact.bonuses.items():
                total[key] = total.get(key, 0) + value
        return total
