import streamlit as st
from moviepy.editor import VideoFileClip 
from io import StringIO

a = st.file_uploader('Upload Videos', type = ['mp4'])
if a is not None:
    video_bytes = a.getvalue()      
    st.video(data = video_bytes)
    # stringio = StringIO(a.getvalue().decode("utf-8"))
    # st.write(stringio)
    
    # # To read file as string:
    # string_data = stringio.read()
    # st.write(string_data)
