#!/usr/bin/env python3
"""
rock-paper-scissors
Feature-rich Rock Paper Scissors game with AI opponent,
win streaks, statistics, tournament mode, and leaderboard.

Author: Sameer Bansal
Reg No: RA2311032010061
College: SRM Institute of Science and Technology
Branch: B.Tech CSE (IoT) | Batch: 2023-2027
"""

import os
import random
import json
import datetime
import time

# ── Constants ─────────────────────────────────────────────
SCORES_FILE = "output/rps_scores.json"

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"

CHOICES = ["rock", "paper", "scissors"]

EMOJIS = {
    "rock": "🪨",
    "paper": "📄",
    "scissors": "✂️ ",
}

# What beats what
BEATS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}

TAUNT_WIN = ["🔥 Destroyed!", "💀 Not even close!", "👑 Dominant!", "🎯 Perfect read!"]
TAUNT_LOSE = ["😤 Lucky!", "🤖 I'll adapt...", "😮 Unexpected!", "📉 Recalculating..."]
TAUNT_TIE = [
    "🤝 Minds think alike.",
    "♟️ Stalemate.",
    "⚖️ Dead even.",
    "😑 Predictable.",
]


# ── AI Engine ─────────────────────────────────────────────
class AIOpponent:
    """
    3 difficulty levels:
    - Easy   : pure random
    - Medium : remembers your last 3 moves, plays counter 40% of the time
    - Hard   : full frequency analysis + pattern detection + counter-play
    """

    def __init__(self, difficulty: str = "Medium") -> None:
        self.difficulty = difficulty
        self.player_history: list[str] = []
        self.ai_history: list[str] = []

    def record(self, player_choice: str, ai_choice: str) -> None:
        self.player_history.append(player_choice)
        self.ai_history.append(ai_choice)

    def predict_player(self) -> str:
        """Predict what player will throw based on their history."""
        if len(self.player_history) < 3:
            return random.choice(CHOICES)

        # Frequency analysis
        freq = {c: self.player_history.count(c) for c in CHOICES}
        most_likely = max(freq, key=lambda k: freq[k])

        # Pattern: last 2 moves repeat?
        if (
            len(self.player_history) >= 2
            and self.player_history[-1] == self.player_history[-2]
        ):
            most_likely = self.player_history[-1]

        return most_likely

    def choose(self) -> str:
        if self.difficulty == "Easy":
            return random.choice(CHOICES)

        if self.difficulty == "Medium":
            if random.random() < 0.40:
                predicted = self.predict_player()
                # play what beats the predicted choice
                return next(k for k, v in BEATS.items() if v == predicted)
            return random.choice(CHOICES)

        # Hard: always counter predicted move
        predicted = self.predict_player()
        return next(k for k, v in BEATS.items() if v == predicted)


# ── Score Manager ─────────────────────────────────────────
class ScoreManager:
    def __init__(self) -> None:
        os.makedirs("output", exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"sessions": [], "players": {}}

    def _save(self) -> None:
        with open(SCORES_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def update(
        self,
        player: str,
        wins: int,
        losses: int,
        ties: int,
        best_streak: int,
        difficulty: str,
    ) -> None:
        total = wins + losses + ties
        win_pct = round((wins / total) * 100, 1) if total > 0 else 0.0

        session = {
            "player": player,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_pct": win_pct,
            "best_streak": best_streak,
            "difficulty": difficulty,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.data["sessions"].append(session)

        # Aggregate per player
        p = self.data["players"].setdefault(
            player, {"wins": 0, "losses": 0, "ties": 0, "best_streak": 0, "games": 0}
        )
        p["wins"] += wins
        p["losses"] += losses
        p["ties"] += ties
        p["games"] += total
        p["best_streak"] = max(p["best_streak"], best_streak)
        self._save()

    def leaderboard(self, top: int = 10) -> list:
        players = []
        for name, s in self.data["players"].items():
            total = s["wins"] + s["losses"] + s["ties"]
            pct = round((s["wins"] / total) * 100, 1) if total > 0 else 0
            players.append({**s, "player": name, "win_pct": pct, "total": total})
        return sorted(
            players, key=lambda p: (p["win_pct"], p["best_streak"]), reverse=True
        )[:top]


# ── Display Helpers ───────────────────────────────────────
def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner() -> None:
    print("=" * 52)
    print("        ✂️  ROCK PAPER SCISSORS  🪨")
    print("        Author : Sameer Bansal | RA2311032010061")
    print("        College: SRMIST Kattankulathur")
    print("=" * 52)


def animate_reveal(player_c: str, ai_c: str) -> None:
    print(f"\n  Revealing", end="", flush=True)
    for _ in range(3):
        time.sleep(0.35)
        print(".", end="", flush=True)
    time.sleep(0.2)
    print(f"\n")
    print(f"  You   →  {EMOJIS[player_c]}  {BOLD}{player_c.upper()}{RESET}")
    print(f"  AI    →  {EMOJIS[ai_c]}  {BOLD}{ai_c.upper()}{RESET}")


def result_display(result: str, taunt: str) -> None:
    if result == "win":
        print(f"\n  {GREEN}{BOLD}🏆 YOU WIN!  {taunt}{RESET}")
    elif result == "lose":
        print(f"\n  {RED}{BOLD}💀 AI WINS!  {taunt}{RESET}")
    else:
        print(f"\n  {YELLOW}{BOLD}🤝 TIE!  {taunt}{RESET}")


def score_display(
    player: str, wins: int, losses: int, ties: int, streak: int, best: int
) -> None:
    total = wins + losses + ties
    win_pct = (wins / total * 100) if total > 0 else 0
    print(f"\n  {'─' * 44}")
    print(
        f"  {BOLD}{player:<16}{RESET}  W:{GREEN}{wins}{RESET}  "
        f"L:{RED}{losses}{RESET}  T:{YELLOW}{ties}{RESET}  "
        f"({win_pct:.0f}%)"
    )
    print(
        f"  🔥 Current streak: {CYAN}{streak}{RESET}   "
        f"⭐ Best: {MAGENTA}{best}{RESET}"
    )


def pick_choice() -> str | None:
    """Prompt player, return choice string or None to quit."""
    print(f"\n  {BOLD}YOUR MOVE{RESET}")
    print(f"  [1] {EMOJIS['rock']}  Rock")
    print(f"  [2] {EMOJIS['paper']}  Paper")
    print(f"  [3] {EMOJIS['scissors']}  Scissors")
    print(f"  [s] Show stats   [q] Quit")
    raw = input("\n  → ").strip().lower()

    if raw in ("q", "quit"):
        return None
    if raw in ("s", "stats"):
        return "stats"
    if raw == "1" or raw == "rock":
        return "rock"
    if raw == "2" or raw == "paper":
        return "paper"
    if raw == "3" or raw == "scissors":
        return "scissors"
    return "invalid"


# ── Play One Round ────────────────────────────────────────
def play_round(player_c: str, ai: AIOpponent) -> str:
    """Returns 'win', 'lose', or 'tie'."""
    ai_c = ai.choose()
    animate_reveal(player_c, ai_c)

    if player_c == ai_c:
        result = "tie"
        taunt = random.choice(TAUNT_TIE)
    elif BEATS[player_c] == ai_c:
        result = "win"
        taunt = random.choice(TAUNT_WIN)
    else:
        result = "lose"
        taunt = random.choice(TAUNT_LOSE)

    result_display(result, taunt)
    ai.record(player_c, ai_c)
    return result


# ── Tournament Mode ───────────────────────────────────────
def tournament_mode(player: str, ai: AIOpponent, sm: ScoreManager) -> None:
    """Best-of-N tournament."""
    print(f"\n  {BOLD}⚔️  TOURNAMENT MODE{RESET}")
    print("  Win more than half the rounds to win the tournament.")
    print("  [1] Best of 3   [2] Best of 5   [3] Best of 7")
    choice = input("  → ").strip()
    total_map = {"1": 3, "2": 5, "3": 7}
    total_rounds = total_map.get(choice, 5)
    to_win = total_rounds // 2 + 1

    p_wins = 0
    ai_wins = 0
    round_num = 0

    while p_wins < to_win and ai_wins < to_win:
        round_num += 1
        clear()
        banner()
        print(f"\n  {BOLD}TOURNAMENT  Round {round_num}/{total_rounds}{RESET}")
        print(
            f"  You: {GREEN}{p_wins}{RESET}  AI: {RED}{ai_wins}{RESET}  "
            f"(First to {to_win})"
        )

        c = pick_choice()
        if c is None or c == "stats":
            print(f"  {YELLOW}Tournament ended early.{RESET}")
            return
        if c == "invalid":
            print(f"  {YELLOW}Invalid choice.{RESET}")
            continue

        result = play_round(c, ai)
        if result == "win":
            p_wins += 1
        elif result == "lose":
            ai_wins += 1
        time.sleep(1.5)

    clear()
    banner()
    if p_wins > ai_wins:
        print(f"\n  {GREEN}{BOLD}🏆 TOURNAMENT WINNER: {player}! 🎉{RESET}")
    else:
        print(f"\n  {RED}{BOLD}💀 TOURNAMENT WINNER: AI  😤{RESET}")

    print(f"  Final: {player} {p_wins} – {ai_wins} AI")
    sm.update(player, p_wins, ai_wins, 0, p_wins, ai.difficulty)
    input("\n  Press ENTER to continue...")


# ── Quick Play ────────────────────────────────────────────
def quick_play(player: str, ai: AIOpponent, sm: ScoreManager) -> None:
    wins = 0
    losses = 0
    ties = 0
    streak = 0
    best_streak = 0

    clear()
    banner()
    print(f"\n  {GREEN}Quick Play  –  Difficulty: {BOLD}{ai.difficulty}{RESET}")
    print(f"  Type your move or [q] to quit.\n")

    while True:
        score_display(player, wins, losses, ties, streak, best_streak)
        c = pick_choice()

        if c is None:
            break

        if c == "stats":
            board = sm.leaderboard()
            show_leaderboard(board)
            input("\n  Press ENTER to continue...")
            continue

        if c == "invalid":
            print(f"  {YELLOW}⚠️  Enter 1/2/3 or rock/paper/scissors.{RESET}")
            continue

        result = play_round(c, ai)

        if result == "win":
            wins += 1
            streak += 1
            best_streak = max(best_streak, streak)
        elif result == "lose":
            losses += 1
            streak = 0
        else:
            ties += 1

        time.sleep(1.2)

    # Session summary
    total = wins + losses + ties
    if total > 0:
        clear()
        banner()
        win_pct = wins / total * 100
        print(f"\n  {BOLD}SESSION SUMMARY – {player}{RESET}")
        print(f"  {'─' * 38}")
        print(f"  🏆 Wins       : {GREEN}{wins}{RESET}")
        print(f"  💀 Losses     : {RED}{losses}{RESET}")
        print(f"  🤝 Ties       : {YELLOW}{ties}{RESET}")
        print(f"  📊 Win Rate   : {win_pct:.1f}%")
        print(f"  🔥 Best Streak: {CYAN}{best_streak}{RESET}")
        sm.update(player, wins, losses, ties, best_streak, ai.difficulty)


# ── Leaderboard Display ───────────────────────────────────
def show_leaderboard(board: list) -> None:
    print(f"\n  {BOLD}🏆 ALL-TIME LEADERBOARD{RESET}")
    print(f"  {'─' * 58}")
    if not board:
        print(f"  {YELLOW}No scores yet. Play a game!{RESET}")
        return
    print(
        f"  {'#':<4} {'Player':<14} {'W':<5} {'L':<5} {'T':<5} {'Win%':<7} {'Streak'}"
    )
    print(f"  {'─' * 58}")
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(board, 1):
        m = medals[i - 1] if i <= 3 else f"  {i}."
        pct_col = GREEN if p["win_pct"] >= 60 else YELLOW if p["win_pct"] >= 40 else RED
        print(
            f"  {m:<4} {p['player']:<14} "
            f"{GREEN}{p['wins']:<5}{RESET}"
            f"{RED}{p['losses']:<5}{RESET}"
            f"{YELLOW}{p['ties']:<5}{RESET}"
            f"{pct_col}{p['win_pct']}%{RESET:<4}  "
            f"{CYAN}{p['best_streak']}{RESET}"
        )


# ── Difficulty Selector ───────────────────────────────────
def select_difficulty() -> str:
    print(f"\n  {BOLD}SELECT AI DIFFICULTY{RESET}")
    print(f"  [1] Easy   – Random AI (beginner-friendly)")
    print(f"  [2] Medium – AI adapts 40% of the time")
    print(f"  [3] Hard   – Full pattern analysis (good luck 😈)")
    choice = input("  → ").strip()
    return {"1": "Easy", "2": "Medium", "3": "Hard"}.get(choice, "Medium")


# ── Main Menu ─────────────────────────────────────────────
def main() -> None:
    clear()
    banner()

    sm = ScoreManager()
    player = input("\n  👤 Enter your name: ").strip() or "Player"

    # Show all-time best if exists
    board = sm.leaderboard()
    pb = next((p for p in board if p["player"] == player), None)
    if pb:
        print(
            f"  🏆 Your best win rate: {CYAN}{pb['win_pct']}%{RESET}  "
            f"Best streak: {MAGENTA}{pb['best_streak']}{RESET}"
        )

    diff = select_difficulty()
    ai = AIOpponent(difficulty=diff)

    while True:
        clear()
        banner()
        print(
            f"\n  {GREEN}Welcome, {BOLD}{player}{RESET}{GREEN}!{RESET}  "
            f"AI: {CYAN}{diff}{RESET}\n"
        )
        print(f"  [1] Quick Play  (unlimited rounds)")
        print(f"  [2] Tournament  (best of 3 / 5 / 7)")
        print(f"  [3] Leaderboard")
        print(f"  [4] Change difficulty")
        print(f"  [q] Quit")

        choice = input("\n  → ").strip().lower()

        if choice == "q":
            print(f"\n  👋 Goodbye, {player}! Practice makes perfect.\n")
            break
        elif choice == "1":
            quick_play(player, ai, sm)
            input("\n  Press ENTER to return to menu...")
        elif choice == "2":
            tournament_mode(player, ai, sm)
        elif choice == "3":
            show_leaderboard(sm.leaderboard())
            input("\n  Press ENTER to return to menu...")
        elif choice == "4":
            diff = select_difficulty()
            ai = AIOpponent(difficulty=diff)
            print(f"  {GREEN}✅ Difficulty set to {BOLD}{diff}{RESET}")
            time.sleep(0.8)
        else:
            print(f"  {YELLOW}⚠️  Invalid choice.{RESET}")
            time.sleep(0.6)


if __name__ == "__main__":
    main()
