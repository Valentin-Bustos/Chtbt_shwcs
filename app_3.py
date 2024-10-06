# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 20:23:09 2024

@author: Valentin
"""
import re
import streamlit as st
from openai import OpenAI

# Load API key and prompts
api_key = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/API Keys/OpenAI key.txt', 'r').read()

# Single Model Prompts
s_Zero = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/Zero Shot/Zero Shot Single Model.txt', 'r').read()
s_Few = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/Multi Shot/Few Shot Single Model.txt', 'r').read()

# Dual Model Chatbot Prompts
d_cb_zero = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/Zero Shot/Zero Shot Dual Model.txt', 'r').read()
d_cb_few = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/Multi Shot/Few Shot Dual Model.txt', 'r').read()

# Dual Model Classifier Prompts
d_cl_zero = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/Evaluator Prompt/Zero_Shot_Dual_Model_Intergration_Prompt.txt', 'r').read()
d_cl_few = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/Evaluator Prompt/Few_Shot_Dual_Model_Intergration_Prompt.txt', 'r').read()

# High Risk Prompt
h_r_prompt = open(r'C:/Users/Valentin/OneDrive - Victoria University of Wellington - STUDENT/CBNS580/Prompts/High Risk Prompt/High risk Prompt.txt', 'r').read()

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
    
    
    # Create an empty container for chat display
    chat_container = st.empty()

    # Display the chat history dynamically, ensuring the latest messages are shown
    chat_history_str = "\n\n".join([f"{entry['role'].capitalize()}: {entry['content']}" for entry in st.session_state.chat])
    chat_container.text_area("Conversation", value=chat_history_str, height=400, disabled=True)

    # Input for user to chat
    user_input = st.text_input("Your message:")
    
    if st.button("Send"):
        st.session_state.chat.append({'role':'user','content':user_input})
        st.session_state.chat_history.append({'role':'user','content':user_input})
        st.session_state.classification_history.append({'role':'user','content':user_input})
        # Here, you'd call your API to get the chatbot response
        if st.session_state.selected_model == 'single':
            # Interact with single model chatbot
            response = s_chatbot.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.chat_history
                )
            res = response.choices[0].message.content
            st.session_state.chat.append({'role': 'Chatbot', 'content': res})
            st.session_state.chat_history.append({'role': 'assistant', 'content': res})
            
            
        elif st.session_state.selected_model == 'dual':
            # Interact with dual model chatbot
            response = d_cb.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.chat_history
                )
            res = response.choices[0].message.content
            st.session_state.chat_history.append({'role': 'assistant', 'content': res})
            st.session_state.chat.append({'role': 'Chatbot', 'content': res})
            classification = d_cl.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.classification_history
                )
            classifier_response = classification.choices[0].message.content
            st.session_state.classification_history.append({'role': 'assistant', 'content': classifier_response})
            st.session_state.chat.append({'role': 'Classifier', 'content': classifier_response})
            
            risk_value_match = re.search(r"\d+(\.\d+)?", classifier_response)
            if risk_value_match:
                if st.session_state.risk_val < 3:
                    st.session_state.risk_val = float(risk_value_match.group(0))
                    if st.session_state.risk_val > 2:
                        system_prompt = h_r_prompt
                        st.session_state.classification_history.append({"role": "assistant", "content": "[HIGH RISK SYSTEM PROMPT NOW IN USE]"})
                        st.session_state.chat.append({'role': 'Classifier', 'content': '[HIGH RISK SYSTEM PROMPT NOW IN USE]'})
            
        # Refresh the chat display after sending a message
        chat_history_str = "\n\n".join([f"{entry['role'].capitalize()}: {entry['content']}" for entry in st.session_state.chat])
        chat_container.text_area("Conversation", value=chat_history_str, height=400, disabled=True)
        
        st.rerun()




