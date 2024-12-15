from src.mcqgenerator.mcqgen import McqGen
import json
import re

def get_setup_input() -> any:
    number = int(input("Number of Questions: "))

    if number  <=  0:
        raise ValueError("Invalid number of Questions")

    url = input("Insert your LinkedIn Account URL: ").strip()

    difficulty = input("Difficulty of the Quiz (easy, medium, hard): ")

    if str.lower(difficulty).strip() not in  ['easy', 'medium', 'hard']:
        raise ValueError("Invalid  difficulty level")

    return number , url, difficulty

def check_answer(options, answer: int,correct_answer: str) -> bool:
    if 1 > answer & answer > 4 :
        raise ValueError("Invalid Answer")
    else:
        if options[answer - 1] == correct_answer:
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

        print("\nGenerated Quiz:\n")
        for i, item in enumerate(quiz, 1):
            print(f"Question {i}: {item['question']}")
            print("Options:")
            for j, option in enumerate(item['responses'], 1):
                print(f"  {j}. {option}")
            answer = input("Select the Correct Answer (1,2,3,4): ")
            
            if type(answer) != "str":
                raise ValueError("Invalid Answer")
            
            status=check_answer(item['responses'],int(answer),item['correct'])

            if status:
                print("Correct!\n" + "-" * 50)
            else:
                print(f"Incorrect, the Correct Answer is: {item['correct']}\n" + "-" * 50)

    except Exception as e:
        print(f"Error: {e}")
