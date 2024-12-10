from setuptools import find_packages,setup

setup(
    name='LinkedIn MCQGenerator',
    version='0.0.1',
    author= 'Reema Maen',
    install_requires=['openai','langchain','pydantic','langchain_community','streamlit','python-dotenv','numpy','pytz','spacy','nltk'],
    packages=find_packages()
)