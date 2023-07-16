import streamlit as st
from pymongo import MongoClient
from config import fault_options
from bson.objectid import ObjectId
from streamlit import session_state as ss

@st.cache_resource()
def init_connection():
    return MongoClient(**st.secrets["mongo"])

client = init_connection()

if 'query' not in ss:
    ss.query = {} 

#connect to ultra database
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
    ss.query = {'mission_id': ss.mission_id}
elif filter == 'By Fault Type':
    type = st.selectbox(label= 'Fault type', options = fault_options)
    ss.query = {'type': type}

faults = []
fault_documents = faults_collection.find(ss.query)

for fault in fault_documents:
    faults.append(
        f"{fault['_id']}"
    )

fault_id = st.selectbox(label='Choose fault', options=faults)
if fault_id is not None:
    video_file = open(f"{fault_id}.mp4", 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)