import json
import time
import threading
import random
from playsound import playsound
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

CORRECT_POINTS = 10
WRONG_POINTS = 7

# Event for synchronizing sound playback
sound_event = threading.Event()

def get_user_answer(prompt):
    answer = input(f"\n{prompt} ")
    return answer.strip()

def initialize_game():
    print("Welcome to the Quiz Game!")
    print("---------------------------")
    score = 0
    return score

def load_questions(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data["rounds"]
    except FileNotFoundError:
        print("❌ Error: File not found.")
        return []
    except json.JSONDecodeError:
        print("❌ Error: JSON file is improperly formatted.")
        return []

def load_high_scores(filename="scores.json"):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return []

def save_high_score(name, score, filename="scores.json"):
    scores = load_high_scores(filename)
    timestamp = str(datetime.now())
    scores.append({"name": name, "score": score, "timestamp": timestamp})
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    with open(filename, 'w') as f:
        json.dump(scores, f, indent=4)
    print("\n🎉 Game scores saved!")

def display_leaderboard():
    scores = load_high_scores()
    print("\n🏆 Top Scores\n-----------------")
    for idx, score in enumerate(scores, start=1):
        print(f"{idx}. {score['name']} - {score['score']} points at {score.get('timestamp', 'N/A')}")

def display_round_info(round_name, round_num, total_rounds, score):
    print(f"\n{Fore.CYAN}📘 Round {round_num}/{total_rounds} - {round_name} | Current Score: {score}{Style.RESET_ALL}")
    for i in range(3, 0, -1):
        print(f"{Fore.YELLOW}Starting in {i}...{Style.RESET_ALL}")
        time.sleep(1)

def display_question(question):
    print(f"\nQuestion ({question['type']}): {question['question']}")
    if question['type'] == "multiple-choice":
        for idx, option in enumerate(question['options']):
            label = chr(65 + idx)  # A, B, C, ...
            print(f"{label}. {option}")
    elif question['type'] == "true/false":
        print("Type 'True' or 'False'")
    else:
        print("Please type your answer:")

def play_sound(is_correct):
    sound_file = "correct.mp3" if is_correct else "wrong.mp3"

    def play():
        playsound(sound_file)
        sound_event.set()  # Signal that sound is finished

    sound_event.clear()  # Reset the event before starting
    threading.Thread(target=play, daemon=True).start()

def display_feedback(is_correct, explanation, current_score):
    if is_correct:
        print(f"\n{Fore.GREEN}✅ Correct!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}❌ Incorrect!{Style.RESET_ALL}")
    print(f"Explanation: {explanation}")
    print(f"Your current score: {current_score}\n")
    time.sleep(1)

def check_answer(user_answer, correct_answer, question_type, current_score, question):
    is_correct = False
    explanation = ""

    if question_type == "multiple-choice":
        try:
            if user_answer.upper() in [chr(65 + i) for i in range(len(question['options']))]:
                user_index = ord(user_answer.upper()) - 65
                user_choice = question['options'][user_index]
            else:
                user_choice = user_answer.strip()
        except:
            user_choice = user_answer.strip()

        correct_choice = question['options'][correct_answer]
        if user_choice.strip().lower() == correct_choice.strip().lower():
            is_correct = True
            explanation = f"The correct answer is {correct_choice}. Well done!"
            current_score += CORRECT_POINTS
        else:
            explanation = f"Sorry, the correct answer was {correct_choice}. Better luck next time!"
            current_score = max(0, current_score - WRONG_POINTS)

    elif question_type == "true/false":
        if str(user_answer).strip().lower() == str(correct_answer).strip().lower():
            is_correct = True
            explanation = f"The correct answer is {correct_answer}. Well done!"
            current_score += CORRECT_POINTS
        else:
            explanation = f"Sorry, the correct answer was {correct_answer}. Better luck next time!"
            current_score = max(0, current_score - WRONG_POINTS)

    elif question_type == "open-ended":
        if user_answer.strip().lower() == correct_answer.strip().lower():
            is_correct = True
            explanation = f"The correct answer is: {correct_answer}"
            current_score += CORRECT_POINTS
        else:
            explanation = f"Sorry, the correct answer was: {correct_answer}"
            current_score = max(0, current_score - WRONG_POINTS)

    display_feedback(is_correct, explanation, current_score)
    play_sound(is_correct)
    sound_event.wait()  # Wait for the sound to finish before proceeding
    return current_score

def show_summary(score, total_questions):
    print("\n📋 Quiz Summary")
    print("----------------------")
    print(f"Total Questions: {total_questions}")
    print(f"Final Score: {score}")
    if score == total_questions * CORRECT_POINTS:
        print("🏅 Perfect Score! Well done!")
    elif score >= total_questions * (CORRECT_POINTS * 0.7):
        print("👏 Great Job!")
    else:
        print("💡 Keep Practicing!")

def game_loop(rounds, score):
    total_rounds = len(rounds)
    for round_num, round_data in enumerate(rounds, start=1):
        round_name = round_data.get("name", f"Round {round_num}")
        timer = round_data.get("timer")
        questions = round_data["questions"]

        def play_questions():
            nonlocal score

            # Track the time taken for Round 1 (Rapid Fire)
            if round_num == 1:
                start_time = time.time()

            display_round_info(round_name, round_num, total_rounds, score)
            for idx, question in enumerate(questions, start=1):
                display_question(question)
                user_answer = get_user_answer("Your answer:")
                score = check_answer(user_answer or "", question['answer'], question['type'], score, question)

            if round_num == 1:
                end_time = time.time()
                time_taken = round(end_time - start_time, 2)
                print(f"\n⏳ Round 1 completed in {time_taken} seconds!")

        play_questions()

        if round_num < total_rounds:
            continue_game = input(f"\nDo you want to continue to the next round (Round {round_num+1})? (yes/no): ").strip().lower()
            if continue_game != 'yes':
                print("\n⏳ Exiting the game. Thank you for playing!")
                break
    return score

def choose_category():
    print("\n📚 Choose a Quiz Category:")
    print("1. GK")
    print("2. Entertainment")

    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            return "gk_questions.json"
        elif choice == "2":
            return "entertainment_questions.json"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def main():
    while True:
        name = input("Enter your name: ").strip()
        print(f"\n🎉 Welcome, {name}! Let's start the quiz!")

        category_file = choose_category()

        score = initialize_game()
        rounds = load_questions(category_file)
        if not rounds:
            print("No questions loaded. Exiting game.")
        else:
            final_score = game_loop(rounds, score)
            show_summary(final_score, sum(len(r['questions']) for r in rounds))
            save_high_score(name, final_score)
            display_leaderboard()

        replay = input("\n🔁 Do you want to play again? (yes/no): ").strip().lower()
        if replay not in ['yes', 'y']:
            print("\n👋 Thanks for playing! See you next time!")
            break


if __name__ == "__main__":
    main()