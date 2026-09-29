from dataclasses import dataclass

from social.relationship import Relationship


@dataclass(frozen=True)
class RelationshipDelta:
    trust: int = 0
    affinity: int = 0
    familiarity: int = 0
    cooperation: int = 0
    conflict: int = 0


class RelationshipUpdatePolicy:
    _DELTAS = {
        "help": RelationshipDelta(trust=8, affinity=5, familiarity=3, cooperation=5),
        "conversation": RelationshipDelta(trust=1, affinity=2, familiarity=4),
        "conflict": RelationshipDelta(trust=-8, affinity=-5, familiarity=2, conflict=10),
        "letter": RelationshipDelta(trust=1, familiarity=2),
    }

    def apply(self, relationship: Relationship, interaction: str) -> Relationship:
        delta = self._DELTAS.get(interaction, RelationshipDelta(familiarity=1))
        relationship.trust = max(-100, min(100, relationship.trust + delta.trust))
        relationship.affinity = max(-100, min(100, relationship.affinity + delta.affinity))
        relationship.familiarity = max(0, min(100, relationship.familiarity + delta.familiarity))
        relationship.cooperation = max(0, min(100, relationship.cooperation + delta.cooperation))
        relationship.conflict = max(0, min(100, relationship.conflict + delta.conflict))
        return relationship

