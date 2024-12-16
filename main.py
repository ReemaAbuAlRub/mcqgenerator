from src.mcqgenerator.mcqgen import McqGen
import json
import re


def get_setup_input() -> any:
    number = int(input("Number of Questions: "))

    if number <= 0 | number > 50:
        raise ValueError("Invalid number of Questions")

    url = input("Insert your LinkedIn Account URL: ").strip()

    if not url:
        raise ValueError("URL is empty")

    difficulty = input("Difficulty of the Quiz (easy, medium, hard): ")

    if str.lower(difficulty).strip() not in ['easy', 'medium', 'hard']:
        raise ValueError("Invalid  difficulty level")

    return number, url, difficulty

def check_answer(options: list, answer: int, correct_answer: str) -> bool:
    if options[answer - 1] == correct_answer:
        return True
    else:
        return False

def clean_output(json_string):
    cleaned_quiz_response = re.sub(r'```[a-zA-Z]*\n|\n```', '', json_string).strip()
    return  json.loads(cleaned_quiz_response)

def print_quiz(quiz):
    print("\nGenerated Quiz:\n")
    for i, item in enumerate(quiz, 1):
        print(f"Question {i}: {item['question']}")
        print("Options:")
        for j, option in enumerate(item['responses'], 1):
            print(f"  {j}. {option}")
        answer = int(input("Select the Correct Answer (Insert 1,2,3,4): "))

        if answer not in range(1,5):
            raise ValueError("Invalid Answer")

        status = check_answer(item['responses'], answer, item['correct'])

        if status:
            print("Correct!\n" + "-" * 50)
        else:
            print(f"Incorrect, the Correct Answer is: {item['correct']}\n" + "-" * 50)

def main():
    try:
        generator = McqGen()
        number, url, difficulty = get_setup_input()
        quiz_response = generator.generate_quiz(
            number=number,
            url=url,
            difficulty=difficulty
        )

        quiz=clean_output(quiz_response["quiz"])
        print_quiz(quiz)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()