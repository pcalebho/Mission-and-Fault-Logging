import streamlit as st
import datetime
import pymongo

st.button('Start Session')

#Entry addition
st.button('Add Entry')


with st.form(key = 'log_entry'):
    st.header('Log Fault')
    fault_name = st.text_input('Fault Name')
    password = st.text_input('Description of fault and what led up to it.')
    st.form_submit_button('Add')


