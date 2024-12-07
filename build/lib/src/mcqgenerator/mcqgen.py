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
        You are an expert Test generator, its your job to generate a quiz of
        {number} questions for professionals based on their skills {skills} found in
        their linkedin accounts in {difficulty} tone. Make sure the questions are not 
        repeated and check that you are testing their knowledge in relation to their skills.
        Make sure you dont include their job titles or company names in the questions.
        Make sure you dont question their experience, ask questions related to the aquired skills only.
        Make sure to make {number} of questions.

        Output should be only a json array with "questions" "responses" and "correct".
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
    quiz_chain=LLMChain(llm=model,prompt=prompt,output_key='quiz',verbose=True)

    return quiz_chain

def llm_chain_answers():
    model=get_llm_model()
    prompt=define_answers_prompt_template()
    answers_chain=LLMChain(llm=model,prompt=prompt,output_key='answers',verbose=True)

    return answers_chain

def create_sequential_chain():
    quiz_chain=llm_chain_questions()
    answers_chain=llm_chain_answers()
    generate_chain=SequentialChain(chains=[quiz_chain,answers_chain],input_variables=[ "number", "skills", "difficulty"],
                        output_variables=["quiz", "answers"], verbose=True)
    
    return generate_chain


data=fetch_profile_data('https://www.linkedin.com/in/reema-abu-al-rob/')

NUMBER=5
SKILLS= data
DIFFICULTY='hard'

with get_openai_callback() as cb:
    obj=create_sequential_chain()
    response= obj(
        {
            'number':NUMBER,
            'skills':SKILLS,
            'difficulty':DIFFICULTY
            
        }
)

print(cb.total_tokens)
print(cb.prompt_tokens)
print(cb.completion_tokens)
print(cb.total_tokens)
print(response)