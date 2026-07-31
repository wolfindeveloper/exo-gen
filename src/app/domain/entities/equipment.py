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
    artifacts: list[EquippedArtifact] = field(default_factory=list)

    def equip(self, item_id: UUID, bonuses: dict, max_slots: int) -> EquippedArtifact | None:
        if any(a.item_id == item_id for a in self.artifacts):
            raise ArtifactAlreadyEquippedError(item_id)

        replaced_artifact: EquippedArtifact | None = None
        if len(self.artifacts) >= max_slots:
            replaced_artifact = self.artifacts.pop(0)

        self.artifacts.append(EquippedArtifact(
            item_id=item_id,
            bonuses=bonuses,
        ))
        return replaced_artifact

    def unequip(self, item_id: UUID) -> EquippedArtifact:
        idx = next((i for i, a in enumerate(self.artifacts) if a.item_id == item_id), None)
        if idx is None:
            raise ValueError(f"Artifact {item_id} is not equipped")

        return self.artifacts.pop(idx)

    def get_total_bonuses(self) -> dict:
        total: dict[str, float] = {}
        for artifact in self.artifacts:
            for key, value in artifact.bonuses.items():
                total[key] = total.get(key, 0) + value
        return total
