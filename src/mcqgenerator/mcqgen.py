import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain_community.callbacks.manager import get_openai_callback
from src.mcqgenerator.utils import fetch_profile_data
import logging.config

logging.config.fileConfig('logger.config')
logger = logging.getLogger()


env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path=env_path)

class McqGen:

    def __init__(self):
        self.api_key = self.get_api_key()
        self.llm_model = self.get_llm_model()

    @staticmethod
    def get_api_key() -> str :
        return os.getenv('API_KEY')

    def get_llm_model(self) -> ChatOpenAI:
        return ChatOpenAI(openai_api_key=self.api_key, model_name='gpt-4o', temperature=0.3)

    @staticmethod
    def define_quiz_prompt_template() -> PromptTemplate :
        template = """
            You are an expert Test generator, its your job to generate a quiz consisting of
            {number} questions for professionals focusing on the following skills: {skills}.These skills
            were obtained from the professionals LinkedIn accounts. The questions should be appropriate at a {difficulty} level.

            Adhere to the following guidelines:
            1. Ensure that the questions are unique and tests the professional's knowledge in relation to the provided skills.
            2. Do not include their job titles or company names in the questions.
            3. Only ask about the practical applications of the provided skills.
            4. Ensure each question has 4 responses.

            Output:
            Return a JSON array with the following structure:
            [
                {{
                    "question": "Question text",
                    "responses": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct": "Correct answer"
                }},
                ...
            ]

        """
        prompt = PromptTemplate(input_variables=["number", "skills", "difficulty"],template=template)
        return prompt

    @staticmethod
    def define_answers_prompt_template() -> PromptTemplate:
        template = """
            You are an expert in {skills}. Given a quiz for {skills} professionals.
            You need to evaluate the complexity of the question and give a complete analysis of the quiz.
            Based on the answers, give some recommendations to the professional who took the exam along with the areas they need to improve in. 
            Quiz:
            
            {quiz}
    
            Check from an expert in {skills} of the above quiz:
        """
        prompt = PromptTemplate(
            input_variables=["skills", "quiz"],
            template=template)

        return prompt


    def llm_chain_questions(self) -> LLMChain:
        model = self.llm_model
        prompt = self.define_quiz_prompt_template()
        quiz_chain = LLMChain(llm=model, prompt=prompt, output_key='quiz', verbose=False)

        return quiz_chain


    def llm_chain_answers(self) -> LLMChain:
        model = self.llm_model
        prompt = self.define_answers_prompt_template()
        answers_chain = LLMChain(llm=model, prompt=prompt, output_key='answers', verbose=False)
        return answers_chain

    def create_sequential_chain(self) -> SequentialChain:
        quiz_chain = self.llm_chain_questions()
        answers_chain = self.llm_chain_answers()
        generate_chain = SequentialChain(chains=[quiz_chain, answers_chain], input_variables=["number", "skills", "difficulty"], output_variables=["quiz", "answers"], verbose=False)
        return generate_chain

    def generate_quiz(self, number: int, url : str, difficulty: str) -> any:
        with get_openai_callback():
            obj=self.create_sequential_chain()
            response= obj(
                {
                    'number':number,
                    'skills':fetch_profile_data(url),
                    'difficulty':difficulty

                }
            )
        return response


import re  # Import re for regex-based cleanup

if __name__ == "__main__":
    try:
        # Initialize quiz generator
        generator = McqGen()

        # Generate quiz
        quiz_response = generator.generate_quiz(
            number=5,
            url="www.linkedin.com/in/reema-abu-al-rob",
            difficulty="hard"
        )

        # Print raw quiz output for debugging
        print("Raw quiz response:", quiz_response['quiz'])

        # Validate and clean the quiz output
        if not quiz_response.get("quiz") or not quiz_response["quiz"].strip():
            raise ValueError("The 'quiz' key is empty or contains invalid data.")

        # Remove backticks and whitespace using regex
        cleaned_quiz_response = re.sub(r'```[a-zA-Z]*\n|\n```', '', quiz_response["quiz"]).strip()

        # Parse JSON string into a Python object
        quiz = json.loads(cleaned_quiz_response)

        # Print the quiz in a readable format
        print("\nGenerated Quiz:\n" + "-" * 50)
        for i, item in enumerate(quiz, 1):
            print(f"Question {i}: {item['question']}")
            print("Options:")
            for j, option in enumerate(item['responses'], 1):
                print(f"  {j}. {option}")
            answer = input("Enter your Answer: ")
            print(answer)

            print(f"Correct Answer: {item['correct']}\n" + "-" * 50)

    except json.JSONDecodeError as e:
        print(f"Failed to parse 'quiz' as JSON: {e}")
    except Exception as e:
        print(f"Error: {e}")
