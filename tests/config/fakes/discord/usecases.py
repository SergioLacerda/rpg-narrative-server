class DummyRollDice:
    def __init__(self, result="ok"):
        self.result = result

    async def execute(self, expression):
        return self.result


class DummyEndSession:
    def __init__(self, result="Resumo"):
        self.result = result

    async def execute(self, campaign_id):
        return self.result


class DummyNarrative:
    def __init__(self, result="ok", error=None):
        self.result = result
        self.error = error

    async def execute(self, **kwargs):
        if self.error:
            raise self.error
        return self.result


class DummyUsecases:
    def __init__(
        self,
        narrative=None,
        roll_dice=None,
        end_session=None,
    ):
        self.narrative = narrative
        self.roll_dice = roll_dice
        self.end_session = end_session