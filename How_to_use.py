import streamlit as st
import base64
def display_local_gif(filename):
    file_ = open(f"tutorials/{filename}", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" width = "600">',
        unsafe_allow_html=True,
    )

st.title('How to Use')

st.subheader('Create a new mission...')
display_local_gif('Mission_set_1_optimized.gif')
st.divider()

st.subheader('or use an existing one')
display_local_gif('Add_existing_mission_2_optimized.gif')
st.divider()

st.subheader('Add faults to your mission')
display_local_gif('Add_fault_3_optimized.gif')
st.divider()

st.subheader('If you want to get the current time.')
display_local_gif('Get_time_4.gif')
st.divider()

st.subheader('Create clips of all faults in mission')
display_local_gif('Uploading_videos_5.gif')
st.divider()

st.subheader('Review details of faults')
display_local_gif('Review_faults_6_optimized.gif')