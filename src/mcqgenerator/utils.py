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
# from logger import logging

nltk.download('stopwords')
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path=env_path)

def get_linkein_api():
    PASSWORD=os.getenv('PASSWORD')
    EMAIL=os.getenv('EMAIL')
    linkedin = Linkedin(EMAIL,PASSWORD)
    return linkedin

def extract_profile(url):
    sections=[part for part in url.split('/') if part]
    return sections[-1]
 

def fetch_profile_data(url):
    linkedin=get_linkein_api()
    username=extract_profile(url)
    profile = linkedin.get_profile(username)

    try: 
        if profile:
            experience = profile.get('experience', [])
            skills = profile.get('skills', [])
            extras=[]
            
            for job in experience:
                job_title = job.get('title', '')
                description = job.get('description', '')
                extras.append(job_title)
   
                if description:
                    words = description.split()
                    stops = set(stopwords.words('english'))  
                    extras.extend([word for word in words if  word not in stops ]) 
            
            total = list(set([skill.get('name', '') for skill in skills] + extras))
           
            return {
                "experience": experience,
                "skills": total 
            }

        else:
            return {
                "experience": 'NOT FOUND',
                "skills": 'NOT FOUND' 
            }
    except Exception as e:
        logging.error(e)

def get_quiz(quiz_str):
    try:
            quiz_dict=json.loads(quiz_str)
            quiz_table_data=[]
            
            # iterate over the quiz dictionary and extract the required information
            for key,value in quiz_dict.items():
                mcq=value["questions"]
                options=" || ".join(
                    [
                        f"{option}-> {option_value}" for option, option_value in value["responses"].items()
                    
                    ]
                )
                
                correct=value["correct"]
                quiz_table_data.append({"MCQ": mcq,"Choices": options, "Correct": correct})
            
            return quiz_table_data
        
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
    
def create_mcq_dataframe(questions):
    # Assuming questions is a list of dictionaries with question details
    df = pd.DataFrame(questions, columns=['questions', 'responses', 'correct','answers'])
    return df