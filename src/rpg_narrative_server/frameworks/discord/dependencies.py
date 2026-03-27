from dataclasses import dataclass


@dataclass
class BotDependencies:
    roll_dice: any
    narrative: any
    end_session: any
