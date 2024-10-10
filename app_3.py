# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 20:23:09 2024

Modified on Fri Oct 11

@author: Valentin
"""
import re
import os
import streamlit as st
from openai import OpenAI

# Load API key and prompts
api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Single Model Prompts
s_Zero = open(r'Prompts/Zero Shot/Zero Shot Single Model.txt', 'r').read()
s_Few = open(r'Prompts/Multi Shot/Few Shot Single Model.txt', 'r').read()

# Dual Model Chatbot Prompts
d_cb_zero = open(r'Prompts/Zero Shot/Zero Shot Dual Model.txt', 'r').read()
d_cb_few = open(r'Prompts/Multi Shot/Few Shot Dual Model.txt', 'r').read()

# Dual Model Classifier Prompts
d_cl_zero = open(r'Prompts/Evaluator Prompt/Zero_Shot_Dual_Model_Intergration_Prompt.txt', 'r').read()
d_cl_few = open(r'Prompts/Evaluator Prompt/Few_Shot_Dual_Model_Intergration_Prompt.txt', 'r').read()

# High Risk Prompt
h_r_prompt = open(r'Prompts/High Risk Prompt/High risk Prompt.txt', 'r').read()

# OpenAI Client
s_chatbot = OpenAI(api_key=api_key)
d_cb = OpenAI(api_key=api_key)
d_cl = OpenAI(api_key=api_key)

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'classification_history' not in st.session_state:
    st.session_state.classification_history = []
if 'chat' not in st.session_state:
    st.session_state.chat = []
st.session_state.risk_val = 0

# Streamlit app logic using session state to handle layers
# Layer 1: Select Model Infrastructure
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = None

if st.session_state.selected_model is None:
    st.title("Select Model Infrastructure")
    if st.button("Single Model"):
        st.session_state.selected_model = 'single'
    if st.button("Dual Model"):
        st.session_state.selected_model = 'dual'

# Layer 2: Select Prompt Type
if st.session_state.selected_model is not None and 'selected_prompt' not in st.session_state:
    st.title("Select Prompt Type")

    if st.session_state.selected_model == 'single':
        if st.button("Zero Shot"):
            st.session_state.selected_prompt = s_Zero
            st.session_state.chat_history = [{'role':'system', 'content':s_Zero}]
            st.session_state.chat = [{'role':'Chatbot System Prompt', 'content':s_Zero}]
        if st.button("Few Shot"):
            st.session_state.selected_prompt = s_Few
            st.session_state.chat_history = [{'role':'system', 'content':s_Few}]
            st.session_state.chat = [{'role':'Chatbot System Prompt', 'content':s_Few}]
    elif st.session_state.selected_model == 'dual':
        if st.button("Zero Shot"):
            st.session_state.selected_prompt = d_cb_zero
            st.session_state.chat_history = [{'role':'system', 'content':d_cb_zero}]
            st.session_state.chat = [{'role':'Chatbot System Prompt', 'content':d_cb_zero}]
            st.session_state.classification_history = [{'role':'system', 'content':d_cl_zero}]
            st.session_state.chat.append({'role':'Classifier System Prompt', 'content':d_cl_zero})
        if st.button("Few Shot"):
            st.session_state.selected_prompt = d_cb_few
            st.session_state.chat_history = [{'role':'system', 'content':d_cb_few}]
            st.session_state.chat = [{'role':'Chatbot System Prompt', 'content':d_cb_few}]
            st.session_state.classification_history = [{'role':'system', 'content':d_cl_few}]
            st.session_state.chat.append({'role':'Classifier System Prompt', 'content':d_cl_few})

# Layer 3: Chat Interface
if 'selected_prompt' in st.session_state:
    st.title("Chat Interface")
    st.write(f"Model: {st.session_state.selected_model.capitalize()} Model")
    st.write(f"Prompt Type: {'Zero Shot' if 'Zero Shot' in st.session_state.selected_prompt else 'Few Shot'}")

    # Display previous chat history using the new streamlit chat interface
    for message in st.session_state.chat:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Input for user to chat
    if prompt := st.chat_input("Your message:"):
        # Append user's message to chat and session state
        st.session_state.chat.append({'role': 'user', 'content': prompt})
        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        st.session_state.classification_history.append({'role': 'user', 'content': prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get the assistant's response
        if st.session_state.selected_model == 'single':
            # Interact with single model chatbot
            with st.chat_message("assistant"):
                stream = s_chatbot.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.chat_history,
                    stream=True
                )
                response = st.write_stream(stream)
            st.session_state.chat.append({'role': 'Chatbot', 'content': response})
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})

        elif st.session_state.selected_model == 'dual':
            # Interact with dual model chatbot
            with st.chat_message("assistant"):
                stream = d_cb.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.chat_history,
                    stream=True
                )
                response = st.write_stream(stream)
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.session_state.chat.append({'role': 'Chatbot', 'content': response})

            # Get classifier response
            with st.chat_message("classifier"):
                classifier_stream = d_cl.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.classification_history,
                    stream=True
                )
                classifier_response = st.write_stream(classifier_stream)
            st.session_state.classification_history.append({'role': 'assistant', 'content': classifier_response})
            st.session_state.chat.append({'role': 'Classifier', 'content': classifier_response})

            # Check for risk values and handle high-risk scenarios
            risk_value_match = re.search(r"\d+(\.\d+)?", classifier_response)
            if risk_value_match:
                if st.session_state.risk_val < 3:
                    st.session_state.risk_val = float(risk_value_match.group(0))
                    if st.session_state.risk_val > 2:
                        # Apply the high-risk prompt if needed
                        system_prompt = h_r_prompt
                        st.session_state.classification_history.append({"role": "system", "content": system_prompt})
                        st.session_state.classification_history.append({"role": "assistant", "content": "[HIGH RISK SYSTEM PROMPT NOW IN USE]"})
                        st.session_state.chat.append({'role': 'Classifier', 'content': '[HIGH RISK SYSTEM PROMPT NOW IN USE]'})

