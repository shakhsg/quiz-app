"""
================================================================================
  QUIZ APPLICATION — Terminal-Based Interactive Quiz Game
================================================================================
  Author      : [Your Name]
  Version     : 1.0.0
  Language    : Python 3.x
  Description :
      A fully interactive, timed command-line quiz application built in Python.
      Players can choose from three categories — General Knowledge, Science,
      and Technology — and race against the clock to answer multiple-choice
      questions. Scores are tracked, results are graded, and players can
      replay as many times as they like.

  Features    :
      - Main menu with navigation
      - 3 quiz categories with 5 questions each
      - Per-question countdown timer (runs in a background thread)
      - Score tracking with percentage and grade feedback
      - Input validation to prevent crashes
      - Replay option after each round

  How to Run  :
      $ python quiz_app.py

  Suitable for a student portfolio / GitHub showcase project.
================================================================================
"""

import time
import threading
import sys
import os
import random

# ──────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

TIME_LIMIT = 15          # Seconds allowed per question
SEPARATOR  = "─" * 60   # Visual divider used throughout the UI


# ──────────────────────────────────────────────────────────────────────────────
#  QUESTION BANK
#  Each question is a dict with:
#    "question"  → the question text
#    "options"   → list of 4 answer choices (A–D)
#    "answer"    → the correct option letter ("A", "B", "C", or "D")
# ──────────────────────────────────────────────────────────────────────────────

QUESTIONS = {
    "General Knowledge": [
        {
            "question": "What is the capital city of Australia?",
            "options":  ["A. Sydney", "B. Melbourne", "C. Canberra", "D. Brisbane"],
            "answer":   "C"
        },
        {
            "question": "How many continents are there on Earth?",
            "options":  ["A. 5", "B. 6", "C. 8", "D. 7"],
            "answer":   "D"
        },
        {
            "question": "Which language is spoken in Brazil?",
            "options":  ["A. Spanish", "B. Portuguese", "C. French", "D. English"],
            "answer":   "B"
        },
        {
            "question": "Who painted the Mona Lisa?",
            "options":  ["A. Michelangelo", "B. Vincent van Gogh", "C. Leonardo da Vinci", "D. Pablo Picasso"],
            "answer":   "C"
        },
        {
            "question": "What is the largest ocean on Earth?",
            "options":  ["A. Atlantic Ocean", "B. Indian Ocean", "C. Arctic Ocean", "D. Pacific Ocean"],
            "answer":   "D"
        },
        {
            "question": "In which year did World War II end?",
            "options":  ["A. 1943", "B. 1944", "C. 1945", "D. 1946"],
            "answer":   "C"
        },
        {
            "question": "What is the currency of Japan?",
            "options":  ["A. Yuan", "B. Won", "C. Ringgit", "D. Yen"],
            "answer":   "D"
        },
    ],

    "Science": [
        {
            "question": "What is the chemical symbol for water?",
            "options":  ["A. WO", "B. HO", "C. H2O", "D. W2O"],
            "answer":   "C"
        },
        {
            "question": "What planet is known as the Red Planet?",
            "options":  ["A. Saturn", "B. Mars", "C. Jupiter", "D. Venus"],
            "answer":   "B"
        },
        {
            "question": "What gas do plants absorb from the atmosphere?",
            "options":  ["A. Oxygen", "B. Nitrogen", "C. Carbon Dioxide", "D. Hydrogen"],
            "answer":   "C"
        },
        {
            "question": "How many bones are in the adult human body?",
            "options":  ["A. 186", "B. 206", "C. 216", "D. 226"],
            "answer":   "B"
        },
        {
            "question": "What is the powerhouse of the cell?",
            "options":  ["A. Nucleus", "B. Ribosome", "C. Mitochondria", "D. Chloroplast"],
            "answer":   "C"
        },
        {
            "question": "What is the speed of light (approx.) in km/s?",
            "options":  ["A. 150,000", "B. 200,000", "C. 300,000", "D. 400,000"],
            "answer":   "C"
        },
        {
            "question": "Which element has the atomic number 1?",
            "options":  ["A. Helium", "B. Carbon", "C. Oxygen", "D. Hydrogen"],
            "answer":   "D"
        },
    ],

    "Technology": [
        {
            "question": "What does 'CPU' stand for?",
            "options":  ["A. Central Process Unit", "B. Central Processing Unit",
                         "C. Computer Personal Unit", "D. Core Processing Unit"],
            "answer":   "B"
        },
        {
            "question": "Which company created the Python programming language?",
            "options":  ["A. Google", "B. Microsoft", "C. Python Software Foundation", "D. Oracle"],
            "answer":   "C"
        },
        {
            "question": "What does 'HTML' stand for?",
            "options":  ["A. Hyper Transfer Markup Language",
                         "B. High Text Markup Language",
                         "C. Hyper Text Markup Language",
                         "D. Hyper Text Modern Language"],
            "answer":   "C"
        },
        {
            "question": "Which of these is NOT a programming language?",
            "options":  ["A. Swift", "B. Kotlin", "C. Photon", "D. Rust"],
            "answer":   "C"
        },
        {
            "question": "What does 'RAM' stand for?",
            "options":  ["A. Random Access Memory", "B. Read Access Memory",
                         "C. Run Access Module", "D. Random Array Module"],
            "answer":   "A"
        },
        {
            "question": "Which company developed the Android operating system?",
            "options":  ["A. Apple", "B. Samsung", "C. Google", "D. Microsoft"],
            "answer":   "C"
        },
        {
            "question": "What is the base (radix) of the binary number system?",
            "options":  ["A. 8", "B. 10", "C. 16", "D. 2"],
            "answer":   "D"
        },
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
#  HELPER — CLEAR SCREEN
# ──────────────────────────────────────────────────────────────────────────────

def clear_screen():
    """Clear the terminal for a clean look on any OS."""
    os.system("cls" if os.name == "nt" else "clear")


# ──────────────────────────────────────────────────────────────────────────────
#  HELPER — PRINT BANNER
# ──────────────────────────────────────────────────────────────────────────────

def print_banner():
    """Display the app title banner at the top of the screen."""
    clear_screen()
    print(SEPARATOR)
    print("       🎯  QUIZ APPLICATION  🎯")
    print("       Test Your Knowledge & Beat the Clock!")
    print(SEPARATOR)
    print()


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 1 — MAIN MENU
# ──────────────────────────────────────────────────────────────────────────────

def show_main_menu():
    """Display the main menu and return the user's validated choice."""
    print_banner()
    print("  MAIN MENU\n")
    print("  [1]  Start Quiz")
    print("  [2]  View Rules")
    print("  [3]  Exit")
    print()
    print(SEPARATOR)

    while True:
        choice = input("  Enter your choice (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return choice
        print("  ⚠  Invalid input. Please enter 1, 2, or 3.")


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 2 — VIEW RULES
# ──────────────────────────────────────────────────────────────────────────────

def show_rules():
    """Display the quiz rules clearly."""
    print_banner()
    print("  📋  QUIZ RULES\n")
    print(f"  1. Choose a category to begin.")
    print(f"  2. Each question is multiple choice (A / B / C / D).")
    print(f"  3. You have {TIME_LIMIT} seconds to answer each question.")
    print(f"  4. Unanswered questions are marked incorrect.")
    print(f"  5. Your score and grade are shown at the end.")
    print(f"  6. You may replay as many times as you like.")
    print()
    print(SEPARATOR)
    input("  Press ENTER to return to the menu...")


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 3 — CATEGORY SELECTION
# ──────────────────────────────────────────────────────────────────────────────

def choose_category():
    """Let the player pick a quiz category. Returns the category name."""
    print_banner()
    categories = list(QUESTIONS.keys())

    print("  SELECT A CATEGORY\n")
    for i, name in enumerate(categories, start=1):
        count = len(QUESTIONS[name])
        print(f"  [{i}]  {name}  ({count} questions)")
    print()
    print(SEPARATOR)

    while True:
        choice = input(f"  Enter your choice (1-{len(categories)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            return categories[int(choice) - 1]
        print(f"  ⚠  Please enter a number between 1 and {len(categories)}.")


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 4 — LOAD QUESTIONS
#  Returns a shuffled copy of 5 questions from the selected category.
# ──────────────────────────────────────────────────────────────────────────────

def load_questions(category, num_questions=5):
    """
    Load and shuffle questions for the given category.

    Args:
        category      (str): The chosen category name.
        num_questions (int): Number of questions to pull (default 5).

    Returns:
        list: A shuffled list of question dicts.
    """
    pool = QUESTIONS.get(category, [])
    return random.sample(pool, min(num_questions, len(pool)))


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 5 — TIMER (runs in a background thread)
# ──────────────────────────────────────────────────────────────────────────────

class QuestionTimer:
    """
    A countdown timer that runs in a background thread.
    When the time expires it sets a flag that the question-asking
    loop checks so it can move on automatically.
    """

    def __init__(self, seconds):
        self.seconds      = seconds
        self.time_up      = False       # Flag: True when countdown reaches 0
        self._stop_event  = threading.Event()
        self._thread      = threading.Thread(target=self._countdown, daemon=True)

    def start(self):
        """Start the countdown thread."""
        self._thread.start()

    def stop(self):
        """Signal the thread to stop early (player answered in time)."""
        self._stop_event.set()

    def _countdown(self):
        """Internal: sleep 1 s at a time and set time_up when done."""
        for _ in range(self.seconds):
            if self._stop_event.is_set():
                return          # Player answered — bail out cleanly
            time.sleep(1)
        if not self._stop_event.is_set():
            self.time_up = True


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 6 — ASK A SINGLE QUESTION
# ──────────────────────────────────────────────────────────────────────────────

def ask_question(q_data, q_number, total):
    """
    Display one question, run the timer, and collect the player's answer.

    Args:
        q_data    (dict): The question dict (question / options / answer).
        q_number  (int) : Current question number (1-based).
        total     (int) : Total number of questions in this round.

    Returns:
        bool: True if the answer was correct, False otherwise.
    """
    clear_screen()
    print(SEPARATOR)
    print(f"  Question {q_number} of {total}  |  ⏱  {TIME_LIMIT} seconds")
    print(SEPARATOR)
    print()
    print(f"  {q_data['question']}")
    print()
    for option in q_data["options"]:
        print(f"    {option}")
    print()
    print(SEPARATOR)

    # Start the background timer
    timer = QuestionTimer(TIME_LIMIT)
    timer.start()

    player_answer = None

    # Keep prompting until a valid key or time runs out
    while not timer.time_up:
        try:
            raw = input("  Your answer (A/B/C/D): ").strip().upper()
        except EOFError:
            # Non-interactive environment — treat as timeout
            break

        if raw in ("A", "B", "C", "D"):
            player_answer = raw
            timer.stop()
            break
        elif raw == "":
            # Player just hit Enter without typing — remind them
            print("  ⚠  Please type A, B, C, or D.")
        else:
            print("  ⚠  Invalid input. Enter A, B, C, or D.")

    # ── Evaluate result ──────────────────────────────────────────────────────

    correct = q_data["answer"]

    if timer.time_up and player_answer is None:
        # Ran out of time
        print()
        print("  ⏰  TIME'S UP!")
        print(f"  ✗  The correct answer was: {correct}")
        time.sleep(2)
        return False

    if player_answer == correct:
        print()
        print("  ✅  Correct! Well done!")
        time.sleep(1.2)
        return True
    else:
        print()
        print(f"  ❌  Wrong! The correct answer was: {correct}")
        time.sleep(1.8)
        return False


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 7 — RUN THE FULL QUIZ
# ──────────────────────────────────────────────────────────────────────────────

def run_quiz(category):
    """
    Orchestrate the quiz: load questions, loop through them,
    track scores, and return the final (correct, wrong) counts.

    Args:
        category (str): The chosen category name.

    Returns:
        tuple: (correct_count, wrong_count, total_questions)
    """
    questions = load_questions(category)
    total     = len(questions)
    correct   = 0
    wrong     = 0

    # ── Pre-quiz screen ──────────────────────────────────────────────────────
    clear_screen()
    print(SEPARATOR)
    print(f"  📚  Category : {category}")
    print(f"  ❓  Questions: {total}")
    print(f"  ⏱  Time/Q   : {TIME_LIMIT} seconds")
    print(SEPARATOR)
    input("\n  Press ENTER when you're ready to start...")

    # ── Question loop ────────────────────────────────────────────────────────
    for index, q_data in enumerate(questions, start=1):
        result = ask_question(q_data, index, total)
        if result:
            correct += 1
        else:
            wrong += 1

    return correct, wrong, total


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 8 — SHOW FINAL RESULTS
# ──────────────────────────────────────────────────────────────────────────────

def show_results(correct, wrong, total, category):
    """
    Display the final score, percentage, and a grade/feedback message.

    Args:
        correct  (int): Number of correct answers.
        wrong    (int): Number of wrong / timed-out answers.
        total    (int): Total questions attempted.
        category (str): The category that was played.
    """
    percentage = (correct / total) * 100 if total > 0 else 0

    # Determine grade and emoji based on percentage
    if percentage == 100:
        grade   = "Perfect Score! 🏆"
        emoji   = "🌟"
    elif percentage >= 80:
        grade   = "Excellent!"
        emoji   = "🥇"
    elif percentage >= 60:
        grade   = "Good Job!"
        emoji   = "🥈"
    elif percentage >= 40:
        grade   = "Needs Improvement"
        emoji   = "🥉"
    else:
        grade   = "Keep Practising!"
        emoji   = "📖"

    # Build a simple visual progress bar
    filled = int(percentage / 10)       # 0–10 blocks
    bar    = "█" * filled + "░" * (10 - filled)

    clear_screen()
    print(SEPARATOR)
    print("  🎉  QUIZ COMPLETE!")
    print(SEPARATOR)
    print(f"\n  Category  : {category}")
    print(f"  Score     : {correct} / {total}")
    print(f"  Correct   : {correct}  ✅")
    print(f"  Wrong     : {wrong}   ❌")
    print(f"  Progress  : [{bar}] {percentage:.1f}%")
    print(f"\n  Feedback  : {emoji}  {grade}")
    print()
    print(SEPARATOR)


# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE 9 — REPLAY PROMPT
# ──────────────────────────────────────────────────────────────────────────────

def ask_replay():
    """
    Ask the player if they want to play again.

    Returns:
        bool: True if they want to replay, False otherwise.
    """
    while True:
        choice = input("\n  Would you like to play again? (Y/N): ").strip().upper()
        if choice == "Y":
            return True
        elif choice == "N":
            return False
        else:
            print("  ⚠  Please enter Y or N.")


# ──────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT — MAIN GAME LOOP
# ──────────────────────────────────────────────────────────────────────────────

def main():
    """
    Main control flow:
      1. Show the main menu.
      2. Route to the chosen action (start / rules / exit).
      3. After a quiz, show results and offer replay.
      4. Loop until the player chooses to exit.
    """
    while True:
        choice = show_main_menu()

        if choice == "1":
            # ── Start Quiz ───────────────────────────────────────────────────
            category              = choose_category()
            correct, wrong, total = run_quiz(category)
            show_results(correct, wrong, total, category)

            if not ask_replay():
                break

        elif choice == "2":
            # ── View Rules ───────────────────────────────────────────────────
            show_rules()

        elif choice == "3":
            # ── Exit ─────────────────────────────────────────────────────────
            clear_screen()
            print(SEPARATOR)
            print("  Thanks for playing! Goodbye! 👋")
            print(SEPARATOR)
            print()
            sys.exit(0)


# ──────────────────────────────────────────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()