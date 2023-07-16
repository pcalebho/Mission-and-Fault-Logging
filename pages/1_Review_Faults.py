import streamlit as st
from pymongo import MongoClient
from config import fault_options
from bson.objectid import ObjectId
from streamlit import session_state as ss

@st.cache_resource()
# Add this file to connect to your database
# ./streamlit/secrets.toml
# [mongo]
# host = "localhost"
# port = 27017
# username = ""
# password = ""
def init_connection():
    return MongoClient(**st.secrets["mongo"])

client = init_connection()

if 'query' not in ss:
    ss.query = {} 

#connect to database
db = client.project
mission_collection = db.missions
faults_collection = db.faults

def format_mission_options(id):
    '''Converts ObjectId's to readable title'''
    if id == '':
        return ""
    
    doc = mission_collection.find_one({'_id': ObjectId(id)})
    if doc is not None:
        return f"Unit: {doc['unit']} | Description: {doc['description']} | Time: {doc['time']}"
    else:
        return ""

def format_fault_options(id):
    if id == '':
        return ''
    
    doc = faults_collection.find_one({'_id': ObjectId(id)})
    if doc is not None:
        return f"Unit: {doc['unit']} | Description: {doc['description']} \
            | Time: {doc['time']} | Date: {doc['date']}"
    else:
        return ""
    
st.title('Review faults')
review_options = ('By Mission', 'By Fault Type')
filter = st.radio('Choose filter', options=review_options)


if filter == 'By Mission':
    mission_options = []
    mission_documents = mission_collection.find()
    for mission in mission_documents:
        mission_options.append(
            f"{mission['_id']}"
        )
    st.selectbox(label= 'Select Mission', options=mission_options, format_func=format_mission_options, key = 'mission_id')
    ss.query = {'mission_id': ObjectId(ss.mission_id)}
elif filter == 'By Fault Type':
    type = st.selectbox(label= 'Fault type', options = fault_options)
    ss.query = {'type': type}

faults = []
fault_documents = faults_collection.find({'$and':[ss.query, {'hasVideo': True}]})

for fault in fault_documents:
    faults.append(
        f"{fault['_id']}"
    )

fault_id = st.selectbox(label='Choose fault', options=faults,format_func=format_fault_options)
if fault_id is not None:
    try:
        video_file = open(f"clips/{fault_id}.mp4", 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
    except Exception:
        st.error('No video found.')