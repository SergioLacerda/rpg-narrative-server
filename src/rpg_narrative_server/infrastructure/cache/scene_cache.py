from .ttl_cache import TTLCache


class SceneCache:

    def __init__(self, ttl=1200, max_items=500):

        self.cache = TTLCache(ttl, max_items)

    def get_scene(self, campaign_id):

        return self.cache.get(campaign_id)

    def set_scene(self, campaign_id, context):

        self.cache.set(campaign_id, context)
