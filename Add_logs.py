import streamlit as st  
import datetime
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from moviepy.editor import VideoFileClip
from config import fault_options
from streamlit import session_state as ss

@st.cache_resource()
def init_connection():
    return MongoClient("mongodb+srv://pcalebho:UISBvUYTesMft5AX@matcluster.5ygnbeg.mongodb.net/")
    

client = init_connection()
db = client.missions

def preview_db(collection):
    try:
        db.validate_collection(collection)  # Try to validate a collection
    except OperationFailure:  # If the collection doesn't exist
        return None

    list = {
        'Datetime': [],
        'Fault Type': []
    }
    data = db[collection].find()


    for entry in data:
        list['Datetime'] += f"{entry['date']} {entry['time']}"
        print('hello')
        list['Fault Type'] += entry['type']

    df = pd.DataFrame(list)
    df = df.sort_values(by='Datetime',ascending=False)
    df
    return df
        


#Create containers
mission_container = st.container()
col1, col2 = st.columns(spec=[.6, .4])
upload_container = st.container()

mission_name = ""

if 'fault_type' not in st.session_state:
    st.session_state.fault_type = fault_options[0]

if 'date' not in ss:
    ss.date = datetime.datetime.now().date()

if 'time' not in ss:
    ss.time = datetime.datetime.now().time().strftime('%H:%M:%S')

if 'mission' not in ss:
    ss.mission = ''


css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(css, unsafe_allow_html=True)


with mission_container:
    st.subheader('1. Set Mission Description')
    with st.form(key = 'mission_set'):
        st.radio('Robot unit',['3.3','4.1','4.2','4.3'], key ='unit')
        st.markdown('Type in mission name/description. Should be done in snake case, and cannot\
                start with a number. It will be used as a collection name.')
        mission_name = st.text_input('Mission Name/Description', key = 'mission_name')
        mission_set = st.form_submit_button('Set Mission')
        if mission_set and mission_name != '':
            ss.mission = mission_name
            st.success('Mission Set!')


#Entry addition
with col1:
    st.subheader('2. Create Entries')
    disabled = False
    if mission_name == "":
        disabled = True


    str_time = ''
    if st.button('Get datetime', key = 'get_time_btn'):
        raw_time = datetime.datetime.now()
        ss.time = raw_time.time().strftime('%H:%M:%S')
        ss.date = raw_time.date()

    
    with st.form(key = 'log_entry', clear_on_submit=True):
        exception = st.radio(label='Exception/Non-exception Fault', options=('Non-exception','Exception'))        
        date = st.date_input('Date', key = 'date', value = ss.date)
        time = st.text_input('Time', key = 'time', value= ss.time, max_chars=8, help= 'format (HH\:MM\:SS)')
        type = st.selectbox('Fault Type', options=fault_options, key = 'fault_type')
        description = st.text_input('Description of fault and what led up to it.')
        submitted = st.form_submit_button('Add', disabled=disabled) 

        if submitted:
            doc = {
                "exception": exception, 
                "type": type, 
                "description": description, 
                "time": ss.time, 
                "date": str(ss.date)
            }
            db[mission_name].insert_one(doc)

with col2:
    # if preview_table is not None:
    list = {
        'Datetime': [],
        'Fault Type': []
    }

    list_of_collections = db.list_collection_names() 
    st.subheader('')
    st.subheader('Entries')
    if ss.mission in list_of_collections:
        data = db[ss.mission].find()

        for entry in data:
            list['Datetime'].append(f"{entry['date']} {entry['time']}")
            list['Fault Type'].append(entry['type'])

        df = pd.DataFrame(list)
        df = df.sort_values(by='Datetime',ascending=False)

        preview_table = df
        st.table(preview_table)
    else:
        st.write('No entries found')

with upload_container:
    st.subheader('3. Upload Video')
    st.file_uploader('Upload')
    st.button('Create clips')