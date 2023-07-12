import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from moviepy.editor import VideoFileClip

@st.cache_resource()
def init_connection():
    return MongoClient("mongodb+srv://st.secrets.db_username:st.secrets.\
        db_pswd@st.secrets.cluster_name.5ygnbeg.mongodb.net/?retryWrites=true&w=majority")

client = init_connection()
db = client.missions
mission_collection = db.test_mission_collection

with st.form(key = 'mission_set'):
    st.header('Start Session')
    st.markdown('Type in mission name/description. Should be done in snake case, and cannot\
            start with a number. It will be used as a collection name.')
    mission_name = st.text_input('Mission Name/Description')
    st.form_submit_button('Add')

#Entry addition
if st.button('Add Entry',key='add_fault_button'):
    fault_time = datetime.now()
    with st.form(key = 'log_entry'):
        st.header(mission_name)
        header = 'Fault @ ' + fault_time.strftime('%m/%d/%y - %H:%M:%S')
        st.subheader(header)
        fault_name = st.text_input('Fault Name')
        password = st.text_input('Description of fault and what led up to it.')
        st.form_submit_button('Add')

if st.button('Create clips'):
    pass
