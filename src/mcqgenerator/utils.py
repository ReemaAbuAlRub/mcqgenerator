import os
import json
import pandas as pd
import traceback
import nltk
import spacy
from langchain_community.chat_models import openai
from dotenv import load_dotenv
from urllib.parse import urlparse
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain_community.callbacks.manager import get_openai_callback
from nltk.corpus import stopwords
from linkedin_api import Linkedin 
import logging.config

logging.config.fileConfig('logger.config')
logger = logging.getLogger()

nltk.download('stopwords')

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path=env_path)

def get_linkein_api() -> str:
    password=os.getenv('PASSWORD')
    email=os.getenv('EMAIL')
    linkedin = Linkedin(email,password)
    return linkedin


def is_url(input_string: str) -> bool :
    result = urlparse(input_string)
    return all([result.scheme, result.netloc])

def extract_profile(url: str) -> str:
    if is_url(url):
        sections=[part for part in url.split('/') if part]
        return sections[-1]
    else:
        raise ValueError("Invalid URL")
 

def fetch_profile_data(url: str) :
    linkedin = get_linkein_api()
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
        logger.error(e)

