from .base_command import BaseCommand


class CommandRegistry:
    """
    Registry simples e tipado de comandos.
    """

    def __init__(self):
        self._commands: dict[str, BaseCommand] = {}

    def register(self, name: str, command: BaseCommand) -> None:
        self._commands[name] = command

    def get(self, name: str) -> BaseCommand:
        if name not in self._commands:
            raise KeyError(f"Command '{name}' not registered")
        return self._commands[name]

    def all(self) -> dict[str, BaseCommand]:
        return self._commands
