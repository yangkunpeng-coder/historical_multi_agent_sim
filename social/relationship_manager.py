from social.relationship import Relationship


class RelationshipManager:
    def __init__(self, owner_id: str) -> None:
        self.owner_id = owner_id
        self._relationships: dict[str, Relationship] = {}

    def get(self, target_id: str) -> Relationship:
        if target_id not in self._relationships:
            self._relationships[target_id] = Relationship(source=self.owner_id, target=target_id)
        return self._relationships[target_id]

    def all(self) -> list[Relationship]:
        return list(self._relationships.values())

