from dataclasses import dataclass
from typing import Any


@dataclass
class BotDependencies:
    roll_dice: Any
    narrative: Any
    end_session: Any
