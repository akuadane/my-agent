from typing import Literal

from colorama import Fore

from src.agent_core.prompts.composer import compose_prompt
from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.context.context import Context
from src.agent_core.providers.ollama_provider import OllamaProvider
from src.agent_core.main_loop import run_agent
from src.agent_core.tools.tool import Tool, ToolPermission

Sign = Literal["X", "O"]


class TicTacToe:
    """3×3 tic-tac-toe: X moves first, then O."""

    def __init__(self) -> None:
        self._board: list[list[Sign | None]] = [[None, None, None] for _ in range(3)]
        self._current: Sign = "X"

    @property
    def current_player(self) -> Sign:
        return self._current

    def __str__(self) -> str:
        """ASCII rendering of the board (no trailing newline)."""
        lines = []
        for r in range(3):
            cells = []
            for c in range(3):
                v = self._board[r][c]
                cells.append(v if v is not None else " ")
            lines.append(" " + " | ".join(cells) + " ")
        return "\n".join([lines[0], "---+---+---", lines[1], "---+---+---", lines[2]])

    def display(self) -> None:
        """Print the board to stdout."""
        print(self)

    def move(self, row: int, col: int, sign: str) -> bool:
        """
        Place `sign` at (row, col). Returns True if the move was applied.

        Verifies: bounds, empty cell, sign is X or O, and sign matches the current turn.

        Args:
            row: The row of the board to place the sign. Zero-indexed.
            col: The column of the board to place the sign. Zero-indexed.
            sign: The sign to place on the board. "X" or "O".

        Returns:
            True if the move was applied, False otherwise.
        """
        if sign not in ("X", "O"):
            return False
        player: Sign = sign  # narrowed by check above
        if player != self._current:
            return False
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return False
        if self._board[row][col] is not None:
            return False
        if self.winner() is not None or self.is_draw():
            return False

        self._board[row][col] = player
        self._current = "O" if player == "X" else "X"
        return True

    def winner(self) -> Sign | None:
        """Return 'X' or 'O' if they have won; else None."""
        b = self._board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] is not None:
                return b[i][0]
            if b[0][i] == b[1][i] == b[2][i] is not None:
                return b[0][i]
        if b[0][0] == b[1][1] == b[2][2] is not None:
            return b[0][0]
        if b[0][2] == b[1][1] == b[2][0] is not None:
            return b[0][2]
        return None

    def is_draw(self) -> bool:
        return self.winner() is None and all(
            self._board[r][c] is not None for r in range(3) for c in range(3)
        )


def play_game():
    game = TicTacToe()
    GAME_SYSTEM_PROMPT = """
    You are a helpful assistant that can play tic-tac-toe.
    You are playing against the user.
    You are X.
    The user is O.
    You start first.
    You should play the best move possible.
    The board is as follows:
    {game}
    """
    system_prompt = compose_prompt(
        [MAIN_SYSTEM_PROMPT, GAME_SYSTEM_PROMPT.format(game=game)]
    )

    user_prompt = "Your turn."
    context = Context(system_prompt)
    context.add_user_message(user_prompt)
    tools = [Tool(function=game.move, permission=ToolPermission.LOW)]

    ollama_provider = OllamaProvider(model="gemma4:e2b")
    while game.winner() is None and not game.is_draw():
        
        game.display()
        if game.current_player == "O":
            user_input = input("> ")
            if (
                user_input.lower() == "exit"
                or user_input.lower() == "quit"
                or user_input.lower() == "q"
            ):
                break
            user_move = user_input.split(" ")
            game.move(int(user_move[0]), int(user_move[1]), "O")
            context.add_user_message(
                f"User moved to row {user_move[0]}, column {user_move[1]}, sign O"
            )

        else:
            showing_thinking = False
            showing_content = False
            for response in run_agent(context, ollama_provider, tools):
                if response.thinking:
                    if not showing_thinking:
                        print(Fore.YELLOW + "Thinking ... ", end="", flush=True)
                        showing_thinking = True

                    print(Fore.YELLOW + response.thinking, end="", flush=True)

                if response.content:
                    if not showing_content:
                        print("\n")
                        print(Fore.GREEN + "Content ... ", end="", flush=True)
                        showing_content = True
                    print(Fore.GREEN + response.content, end="", flush=True)
                    showing_thinking = False

        print(Fore.RESET + "\n")
        context.add_system_message(f"The board is as follows: {str(game)}")

if __name__ == "__main__":
    play_game()
