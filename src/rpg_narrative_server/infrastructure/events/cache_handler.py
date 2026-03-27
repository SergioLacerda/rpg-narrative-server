from domain.events.response_generated_event import ResponseGeneratedEvent


def register_cache_handler(event_bus, cache):

    def handler(event):
        if not event.prompt or not event.response:
            return

        key = hash(event.prompt)
        cache.set(key, event.response)

    event_bus.subscribe(ResponseGeneratedEvent, handler)
