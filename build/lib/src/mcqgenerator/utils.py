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
import PyPDF2
from nltk.corpus import stopwords
from linkedin_api import Linkedin 
# from logger import logging

nltk.download('stopwords')
load_dotenv()

def get_linkein_api():
    PASSWORD=os.getenv('PASWORD')
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
