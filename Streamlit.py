import os
import json
import traceback
import pandas as pd 
from dotenv import load_dotenv
import streamlit as st 
from src.mcqgenerator.mcqgen import create_sequential_chain,get_openai_callback
from src.mcqgenerator.utils import fetch_profile_data,get_quiz,create_mcq_dataframe
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain


import streamlit as st
st.title('LinkedIn Skill Bsed Quiz Generator')
import json
import traceback

# Function to display a question
def display_question(question_data):
    if isinstance(question_data, dict):
        st.write(question_data.get("question", "Question not found"))
        selected_response = st.radio("Select your answer:", question_data.get("responses", []), key=question_data.get("question", "default_key"))
        return selected_response
    else:
        st.error("Invalid question format.")
        return None

with st.form('input'):
    linkedin_url = st.text_input("LinkedIn URL:")
    num_questions = st.number_input("Insert the Desired Number of Questions", min_value=1, max_value=50)
    difficulty = st.radio("Select the Difficulty Level", ["Easy", "Medium", "Hard"], index=0)
    button = st.form_submit_button("quiz")

    if button and linkedin_url and num_questions and difficulty:
        with st.spinner("Loading Quiz.."):
            try:
                skills = fetch_profile_data(linkedin_url)
                with get_openai_callback() as cb:
                    obj = create_sequential_chain()
                    response = obj({
                        'number': num_questions,
                        'skills': skills,
                        'difficulty': difficulty
                    })
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error while fetching quiz data.")
            else:
                quiz = response.get("quiz")

                # Validate and ensure quiz data is in list format
                if isinstance(quiz, str):
                    try:
                        quiz = json.loads(quiz)
                    except json.JSONDecodeError:
                        st.error("Invalid quiz format: Unable to parse quiz data.")
                        quiz = None

                if isinstance(quiz, dict):
                    quiz = [quiz]  # Convert a single question dictionary to a list

                if not quiz or not isinstance(quiz, list):
                    st.error("Invalid quiz format or no quiz data found.")
                else:
                    st.title("Interactive Quiz App")
                    
                    # Iterate through quiz data and display the question
                    for i, question_data in enumerate(quiz):
                        if not isinstance(question_data, dict):
                            st.error(f"Invalid question data at index {i}")
                            continue

                        st.write(f"Question {i + 1}")
                        selected_response = display_question(question_data)

                        # Check if the answer is correct
                        if selected_response is not None and st.button(f"Submit Answer for Question {i + 1}", key=f"submit_{i}"):
                            correct_answer = question_data.get("correct")
                            if correct_answer is None:
                                st.error("Correct answer not provided for this question.")
                            elif selected_response == correct_answer:
                                st.success("Correct!")
                            else:
                                st.error(f"Wrong answer. The correct answer is: {correct_answer}")
