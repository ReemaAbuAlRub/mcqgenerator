import os
import json
import pandas as pd
import traceback
import nltk
import spacy
from langchain_community.chat_models import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain_community.callbacks.manager import get_openai_callback
from nltk.corpus import stopwords
from linkedin_api import Linkedin  
from src.mcqgenerator.utils import get_linkein_api,extract_profile,fetch_profile_data


load_dotenv()
  
def get_api_key():
    KEY=os.getenv('API_KEY')
    return KEY

def get_llm_model():
    KEY=get_api_key()
    model=ChatOpenAI(openai_api_key=KEY, model_name='gpt-4o',temperature=0.3)
    return model

def define_quiz_generater_prompt_template():

    TEMPLATE = """
        You are an expert Test generator, its your job to generate a quiz consisting of
        {number} questions for professionals focusing on the following skills: {skills}.These skills
        were obtained from the professionals LinkedIn accounts. The questions should be appropriate at a {difficulty} level.
        
        Adhere to the following guidelines:
        1. Ensure that the questions are unique and tests the professional's knowledge in relation to the provided skills.
        2. Do not include their job titles or company names in the questions.
        3. Only ask about the practical applications of the provided skills.
        4. Ensure each question has 4 responses.

        Output:
        The output must be a JSON array containing the following keys:
            1. "questions": The list of questions.
            2. "responses": The list of multiple-choice responses for each question.
            3. "correct": The correct answer for each question.
        
        Example Output:
        ```json
        [
            {
                "question": "What is the primary advantage of using unsupervised machine learning techniques in anomaly detection?",
                "responses": [
                    "They require labeled data for training.",
                    "They can identify patterns without prior knowledge of the data structure.",
                    "They are faster than supervised learning techniques.",
                    "They are less computationally intensive."
                ],
                "correct": "They can identify patterns without prior knowledge of the data structure."
            },
            {
                "question": "Which of the following is a key benefit of using natural language processing (NLP) in text analysis?",
                "responses": [
                    "Faster computation compared to traditional algorithms.",
                    "Ability to understand and derive meaning from human language.",
                    "Increased hardware requirements.",
                    "Reduced accuracy in identifying anomalies."
                ],
                "correct": "Ability to understand and derive meaning from human language."
            }
        ]
    """

    prompt= PromptTemplate(
        install_variables=[ "number", "skills", "difficulty"],
        template=TEMPLATE)

    return prompt

def define_answers_prompt_template():
    TEMPLATE = """
        You are an expert in {skills}. Given a quiz for {skills} professionals.\
        You need to evaluate the complexity of the question and give a complete analysis of the quiz.
        Based on the answers, give some reccomnedations to the professional who took the exam along with the areas they need to improve in. 
        Quiz:
        {quiz}

        Check from an expert in {skills} of the above quiz:
    """
    prompt= PromptTemplate(
        install_variables=[ "skills", "quiz"],
        template=TEMPLATE)

    return prompt


def llm_chain_questions():
    model=get_llm_model()
    prompt=define_quiz_generater_prompt_template()
    quiz_chain=LLMChain(llm=model,prompt=prompt,output_key='quiz',verbose=False)

    return quiz_chain

def llm_chain_answers():
    model=get_llm_model()
    prompt=define_answers_prompt_template()
    answers_chain=LLMChain(llm=model,prompt=prompt,output_key='answers',verbose=False)

    return answers_chain

def create_sequential_chain():
    quiz_chain=llm_chain_questions()
    answers_chain=llm_chain_answers()
    generate_chain=SequentialChain(chains=[quiz_chain,answers_chain],input_variables=[ "number", "skills", "difficulty"],
                        output_variables=["quiz", "answers"], verbose=True)
    
    return generate_chain


# data=fetch_profile_data('https://www.linkedin.com/in/reema-abu-al-rob/')

# NUMBER=5
# SKILLS= data
# DIFFICULTY='hard'

# with get_openai_callback() as cb:
#     obj=create_sequential_chain()
#     response= obj(
#         {
#             'number':NUMBER,
#             'skills':SKILLS,
#             'difficulty':DIFFICULTY
            
#         }
# )

# print(cb.total_tokens)
# print(cb.prompt_tokens)
# print(cb.completion_tokens)
# print(cb.total_tokens)
# print(response)

class McqGen:
    def __init__(self):
        self.api_key = self.get_api_key()
        self.llm_model = self.get_llm_model()

    def get_api_key(self):
        return os.getenv('API_KEY')

    def get_llm_model(self):
        return ChatOpenAI(openai_api_key=self.api_key, model_name='gpt-4o', temperature=0.3)

    def define_quiz_prompt_template(self):
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
            The output must be a JSON array containing the following keys:
                1. "questions": The list of questions.
                2. "responses": The list of multiple-choice responses for each question.
                3. "correct": The correct answer for each question.

            Example Output:
            ```json
            [
                {
                    "question": "What is the primary advantage of using unsupervised machine learning techniques in anomaly detection?",
                    "responses": [
                        "They require labeled data for training.",
                        "They can identify patterns without prior knowledge of the data structure.",
                        "They are faster than supervised learning techniques.",
                        "They are less computationally intensive."
                    ],
                    "correct": "They can identify patterns without prior knowledge of the data structure."
                },
                {
                    "question": "Which of the following is a key benefit of using natural language processing (NLP) in text analysis?",
                    "responses": [
                        "Faster computation compared to traditional algorithms.",
                        "Ability to understand and derive meaning from human language.",
                        "Increased hardware requirements.",
                        "Reduced accuracy in identifying anomalies."
                    ],
                    "correct": "Ability to understand and derive meaning from human language."
                }
            ]
        """
        prompt = PromptTemplate(input_variables=["number", "skills", "difficulty"],template=template)
        return prompt
