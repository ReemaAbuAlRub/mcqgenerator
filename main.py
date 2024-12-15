from src.mcqgenerator.mcqgen import McqGen
import json
import re

def get_setup_input() -> any:
    number = int(input("Number of Questions: "))

    if number  <=  0:
        raise ValueError("Invalid number of Questions")

    url = input("Insert your LinkedIn Account URL: ")

    difficulty = input("Difficulty of the Quiz (easy, medium, hard): ")

    if str.lower(difficulty) not in  ['easy', 'medium', 'hard']:
        raise ValueError("Invalid  difficulty level")

    return number , url, difficulty

def check_answer(answer: str,correct_answer: str) -> bool:
    if answer == correct_answer:
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        generator = McqGen()
        number, url, difficulty = get_setup_input()
        quiz_response = generator.generate_quiz(
            number=number,
            url=url,
            difficulty=difficulty
        )

        cleaned_quiz_response = re.sub(r'```[a-zA-Z]*\n|\n```', '', quiz_response["quiz"]).strip()
        quiz = json.loads(cleaned_quiz_response)

        print("\nGenerated Quiz:\n" + "-" * 50)
        for i, item in enumerate(quiz, 1):
            print(f"Question {i}: {item['question']}")
            print("Options:")
            for j, option in enumerate(item['responses'], 1):
                print(f"  {j}. {option}")
            answer = input("Enter your Answer: ")

            status=check_answer(answer,item['correct'])

            if status:
                print("Correct!\n" + "-" * 50)
            else:
                print(f"Incorrect, the Correct Answer is: {item['correct']}\n" + "-" * 50)

    except Exception as e:
        print(f"Error: {e}")
