import streamlit as st  
import datetime
import pandas as pd
import os
import re
from pymongo import MongoClient
from moviepy.editor import VideoFileClip
from config import fault_options, unit_options
from streamlit import session_state as ss
from bson.objectid import ObjectId

@st.cache_resource()
def init_connection():
    return MongoClient(**st.secrets["mongo"])
    
client = init_connection()

# connect to mongodb database and collections
db = client.project
mission_collection = db.missions
faults_collection = db.faults   

# Create streamlit containers. 
# Streamlit containers help separate the widgets within the webpage.
mission_container = st.container()
col1, col2 = st.columns(spec=[.6, .4])
upload_container = st.container()


# This code iniatilizes necessary session state variables, so the API
# does not throw an error.
if 'fault_type' not in ss:
    st.session_state.fault_type = fault_options[0]
if 'date' not in ss:
    ss.date = datetime.datetime.now().date()
if 'time' not in ss:
    ss.time = datetime.datetime.now().time().strftime('%H:%M:%S')
if 'mission_id' not in ss:
    ss.mission_id = ''
if 'unit' not in ss:
    ss.unit = unit_options[0]
if 'mission_description' not in ss:
    ss.mission_description = ''
if 'mission_submit' not in ss:
    ss.mission_submit = False
if 'btn_new_mission' not in ss:
    ss.btn_new_mission = False
if 'btn_existing_mission' not in ss:
    ss.btn_existing_mission = False

# The statements use css to remove borders from the streamlit form widgets.
css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(css, unsafe_allow_html=True)


def parse_datetime_string(datetime_string):
    '''Converts datetime string into a datetime object'''
    format = '%Y-%m-%d %H:%M:%S'
    try:
        parsed_datetime = datetime.datetime.strptime(datetime_string, format)
        return parsed_datetime
    except ValueError:
        raise ValueError('Invalid datetime string format.')


def format_mission_options(id):
    '''Converts ObjectId's to readable title'''
    if id == '':
        return ""
    
    doc = mission_collection.find_one({'_id': ObjectId(id)})
    if doc is not None:
        return f"Unit: {doc['unit']} | Description: {doc['description']} \
            | Time: {doc['time']}"
    else:
        return ""
    
def is_valid_time_format(time_string):
    '''Checks if a time_string is a valid format or value'''
    pattern = r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$'
    match = re.match(pattern, time_string)
    
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        
        if hours <= 23 and minutes <= 59 and seconds <= 59:
            return True
    
    return False

# This is used for setting the mission for the fault logging.
with mission_container:
    st.subheader('1. Set Missions')
    mission_selection_options = ('Create new mission', 'Use existing mission')
    choice = st.radio('Mission selection', options=mission_selection_options)

    # Presents form to create a new mission.
    # Submitting form creates a new document in the mission collection
    if choice == mission_selection_options[0]:
        with st.form(key = 'mission_set'):
            st.radio('Robot unit',unit_options, key ='unit')
            st.markdown('Type in mission description.')
            st.text_input('Mission Description', key = 'mission_description')
            mission_set = st.form_submit_button('Set Mission')
            if mission_set:
                # Uses the session state of widgets for the inserted document
                mission_document = {
                    'unit': ss.unit,
                    'description': ss.mission_description,
                    'time': datetime.datetime.now(tz=datetime.timezone.utc)
                }
                ss.mission_id = \
                    mission_collection.insert_one(mission_document).inserted_id
                st.success('Mission Set!')
    else:
        # Find mission id's in the mission collection, and collect into list.
        mission_options = []
        mission_documents = mission_collection.find()
        for mission in mission_documents:
            mission_options.append(
                f"{mission['_id']}"
            )

        # Mission ID's are placed in selectbox options. Format function transforms
        # ID into something more meaningful
        ss.mission_id = st.selectbox(
            'Select Mission', 
            options= mission_options,
            format_func=format_mission_options
        )


# This is the fault entry form column
with col1:
    st.subheader('2. Create Entries')

    # This code is used for disabling the form submit button if the mission is not set.
    disabled = False
    if ss.mission_id == '':
        disabled = True

    # Display the 'set mission.' If there is no mission set, print let em know
    if ss.mission_id != '':
        mission_fields = mission_collection.find_one({'_id': ObjectId(ss.mission_id)})
        if mission_fields is not None:
            st.text('Unit: ' + mission_fields['unit'])
            st.text('Description: ' + mission_fields['description'])
            st.text('Time: ' + str(mission_fields['time']))
    else:
        st.text('No mission set')

    # Button to get datetime at button press 
    if st.button('Get datetime', key = 'get_time_btn'):
        raw_time = datetime.datetime.now()
        ss.time = raw_time.time().strftime('%H:%M:%S')
        ss.date = raw_time.date()

    
    with st.form(key = 'log_entry', clear_on_submit=True):
        exception = st.radio(label='Exception/Non-exception Fault', options=('Non-exception','Exception'))        
        date = st.date_input('Date', key = 'date', value = ss.date)
        time = st.text_input('Time', key = 'time', value= ss.time, max_chars=8, help= 'format (HH\:MM\:SS)')
        type = st.selectbox('Fault Type', options=fault_options, key = 'fault_type')
        description = st.text_area('Description of fault and what led up to it.')
        submitted = st.form_submit_button('Add', disabled=disabled) 

        if submitted:
            doc = {
                "mission_id": ObjectId(ss.mission_id),
                "unit": ss.unit,
                "exception": exception, 
                "type": type, 
                "description": description, 
                "time": ss.time, 
                "date": str(ss.date)
            }
            faults_collection.insert_one(doc)

with col2:
    list = {
        'Datetime': [],
        'Fault Type': []
    }

    # Display a table of the last 10 faults in a mission.
    if ss.mission_id != '':
        data = faults_collection.find({'mission_id': ObjectId(ss.mission_id)})

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
        st.write('No entries found.')
        

with upload_container:
    #create cache folder if it does not exist
    if not os.path.isdir('.cache'):
        os.mkdir('.cache')

    if not os.path.isdir('clips'):
        os.mkdir('clips')

    FILE_OUTPUT = '.cache/output.mp4'


    st.subheader('3. Upload Video')
    with st.form(key = 'clip_generator'):
        video = st.file_uploader('Upload', type = ['mp4'])
        start_date_video = st.date_input('Starting date of video')
        time_start_video = st.text_input('Starting time of uploaded video (HH\:MM\:SS)')
        video_submit = st.form_submit_button('Submit')
        if video_submit:
            if video is not None and is_valid_time_format(time_start_video):
                video_bytes = video.getvalue()

                # opens the file 'output.mp4' which is accessable as 'out_file'
                with open(FILE_OUTPUT, "wb") as out_file:  # open for [w]riting as [b]inary
                    out_file.write(video_bytes)

                raw_clip = VideoFileClip(FILE_OUTPUT)        
                video_start = parse_datetime_string(str(start_date_video) + ' ' + time_start_video)
                fault_list = faults_collection.find({'mission_id': ObjectId(ss.mission_id)})
                num_faults = faults_collection.count_documents({'mission_id': ObjectId(ss.mission_id)})
                step = 1.0/num_faults
                
                clip_i = 1
                progress_text = f"Generating Clips ({clip_i}/3)"
                progress_bar = st.progress(0, text=progress_text)
                percent_complete = 0

                for fault in fault_list:
                    fault_datetime = parse_datetime_string(f"{fault['date']} {fault['time']}")
                    time_delta = fault_datetime-video_start
                    seconds = time_delta.total_seconds()
                    clip_start = seconds-10
                    if clip_start < 0:
                        clip_start = 0
                    clip_end = seconds+5
                    clip = raw_clip.subclip(clip_start,clip_end)
                    clip.write_videofile(filename=f"clips/{fault['_id']}.mp4",codec='libx264')
                    faults_collection.find_one_and_update({"_id": ObjectId(fault['_id'])}, {"$set":{"hasVideo":True}})
                    percent_complete += step
                    clip_i += 1
                    if clip_i != 4:
                        progress_text = f"Generating Clips ({clip_i}/3)"
                    else:
                        progress_text = 'Complete!'
                    progress_bar.progress(percent_complete, text=progress_text)
            else:
                st.error('Invalid inputs')