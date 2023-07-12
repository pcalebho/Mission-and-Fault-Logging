import streamlit as st
import datetime
from pymongo import MongoClient
from moviepy.editor import VideoFileClip

@st.experimental_singleton()
def init_connection():
    return MongoClient("mongodb+srv://st.secrets.db_username:st.secrets.\
        db_pswd@st.secrets.cluster_name.5ygnbeg.mongodb.net/?retryWrites=true&w=majority")

st.button('Start Session')

#Entry addition
st.button('Add Entry')


with st.form(key = 'log_entry'):
    st.header('Log Fault')
    fault_name = st.text_input('Fault Name')
    password = st.text_input('Description of fault and what led up to it.')
    st.form_submit_button('Add')


