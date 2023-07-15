import streamlit as st  
import datetime
import pandas as pd
import os
from pymongo import MongoClient
from moviepy.editor import VideoFileClip
from config import fault_options, unit_options
from streamlit import session_state as ss

@st.cache_resource()
def init_connection():
    return MongoClient(**st.secrets["mongo"])
    

client = init_connection()

#connect to ultra database
db = client.ultra
mission_collection = db.missions
faults_collection = db.faults   

#Create containers
mission_container = st.container()
col1, col2 = st.columns(spec=[.6, .4])
upload_container = st.container()

mission_description = ""

if 'fault_type' not in st.session_state:
    st.session_state.fault_type = fault_options[0]

if 'date' not in ss:
    ss.date = datetime.datetime.now().date()

if 'time' not in ss:
    ss.time = datetime.datetime.now().time().strftime('%H:%M:%S')

if 'mission' not in ss:
    ss.mission = ''

if 'unit' not in ss:
    ss.unit = unit_options[0]


css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(css, unsafe_allow_html=True)


with mission_container:
    st.subheader('1. Set Mission Description')
    with st.form(key = 'mission_set'):
        unit = st.radio('Robot unit',unit_options, key ='unit')
        st.markdown('Type in mission name/description. Should be done in snake case, and cannot\
                start with a number. It will be used as a collection name.')
        mission_description = st.text_input('Mission Description', key = 'mission_name')
        mission_set = st.form_submit_button('Set Mission')
        if mission_set and mission_description != '':
            ss.mission = mission_description
            st.success('Mission Set!')


#Entry addition
with col1:
    st.subheader('2. Create Entries')
    disabled = False
    if mission_description == "":
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
                "unit": ss.unit,
                "exception": exception, 
                "type": type, 
                "description": description, 
                "time": ss.time, 
                "date": str(ss.date)
            }
            db[mission_description].insert_one(doc)

with col2:
    # if preview_table is not None:
    list = {
        'Datetime': [],
        'Fault Type': []
    }

    list_of_collections = db.list_collection_names() 
    st.subheader('Entries (recent 10)')
    if ss.mission in list_of_collections:
        data = db[ss.mission].find()

        for entry in data:
            list['Datetime'].append(f"{entry['date']} {entry['time']}")
            list['Fault Type'].append(entry['type'])

        df = pd.DataFrame(list)
        df = df.set_index('Datetime')
        df = df.sort_values(by='Datetime',ascending=False)
        df.index.name = 'Datetime'
        preview_table = df
        if df.shape[0] >= 11:
            st.table(preview_table.head(10))
        else:
            st.table(preview_table)
        
    else:
        st.write('No entries found')

with upload_container:
    #create cache folder if it does not exist
    if not os.path.isdir('.cache'):
        os.mkdir('.cache')

    FILE_OUTPUT = '.cache/output.mp4'

    # Checks and deletes the output file
    # You cant have a existing file or it will through an error
    if os.path.isfile(FILE_OUTPUT):
        os.remove(FILE_OUTPUT)


    st.subheader('3. Upload Video')
    video = st.file_uploader('Upload', type = ['mp4'])
    if video is not None and ss.mission != '':
        video_bytes = video.getvalue()

         # opens the file 'output.mp4' which is accessable as 'out_file'
        with open(FILE_OUTPUT, "wb") as out_file:  # open for [w]riting as [b]inary
            out_file.write(video_bytes)

        raw_clip = VideoFileClip(FILE_OUTPUT)

        st.button('Create clips')