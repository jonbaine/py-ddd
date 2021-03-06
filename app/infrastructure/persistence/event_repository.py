from app.domain.model.Event import Event, EventId, EventName


class EventRepository:
    def persist(self, event) -> None:
        raise NotImplementedError

    def delete(self, event) -> None:
        raise NotImplementedError

    def of_id(self, identifier) -> object:
        raise NotImplementedError

    def all(self) -> list:
        raise NotImplementedError


class MongoEventRepository(EventRepository):
    def __init__(self, mongo_client):
        self.collection = mongo_client.collection('events')

    def persist(self, event) -> None:
        if self.__exist_document(event.identifier.identifier):
            self.collection.update_one(
                {'identifier': event.identifier.identifier},
                {
                    "$set": {
                        'identifier': str(event.identifier.identifier),
                        'name': event.name.name
                    }
                }
            )
        else:
            self.collection.insert_one({
                'identifier': str(event.identifier.identifier),
                'name': event.name.name
            })

        # This action should be launched from a database afterPersist hook if possible
        event.release()

    def delete(self, event) -> None:
        self.collection.delete_one({'identifier': event.identifier})

        # This action should be launched from a database afterPersist hook if possible
        event.release()

    def of_id(self, identifier) -> object:
        result = self.collection.find_one({'identifier': identifier})
        if result is not None:
            return self.__to_instance(
                result
            )
        else:
            return None

    def all(self) -> list:
        events = self.collection.find({})
        return [self.__to_instance(event) for event in events]

    def __exist_document(self, identifier):
        return self.of_id(identifier) is not None

    def __to_instance(self, record):
        return Event(
            EventId(record['identifier']),
            EventName(record['name'])
        )
