import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from moviepy.editor import VideoFileClip

@st.cache_resource()
def init_connection():
    return MongoClient("mongodb+srv://pcalebho:UISBvUYTesMft5AX@matcluster.5ygnbeg.mongodb.net/")

client = init_connection()
db = client.missions

col1, col2 = st.columns(2)

if 'fault_type' not in st.session_state:
    st.session_state.fault_type = ' '

if 'fault_description' not in st.session_state:
    st.session_state.fault_description = ' '


def write_to_db(collection, time, type = None, description = None):
    if type is None and description is None:
        output_type = st.session_state.fault_type
        output_description = st.session_state.fault_description
    else:
        output_type = type
        output_description = description
    document = {"fault_type": output_type, "fault_description": output_description, \
                    "fault_time": time}
    db[collection].insert_one(document)

css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(css, unsafe_allow_html=True)

with col1:
    with st.form(key = 'mission_set'):
        st.radio('Robot unit',['3.3','4.1','4.2','4.3'])
        st.markdown('Type in mission name/description. Should be done in snake case, and cannot\
                start with a number. It will be used as a collection name.')
        mission_name = st.text_input('Mission Name/Description')
        st.form_submit_button('Set Mission')


#Entry addition
with col2:
    fault_time = ''

    if st.button('Get Time'):
        raw_time = datetime.now()
        fault_time = raw_time.strftime('%m/%d/%y - %H:%M:%S')

    with st.form(key = 'log_entry', clear_on_submit=True):
        fault_time = st.text_input('Fault Time', value = fault_time)
        fault_type = st.text_input('Fault Type', key = 'fault_type')
        fault_description = st.text_input('Description of fault and what led up to it.', \
                                                    key = 'fault_description')
        submit_btn = st.form_submit_button('Add') #, on_click= write_to_db(mission_name,\
                                                            #              fault_time))
        if submit_btn:
            doc = {"fault_type": fault_type, "fault_description": fault_description, \
                    "fault_time": fault_time}
            db[mission_name].insert_one(doc)

if mission_name != "":
    pass

if st.file_uploader('Upload video'):
    pass

if st.button('Create clips'):
    pass
