#Import libraries
import streamlit as st
from owlready2 import *
import pandas as pd

# Define Functions to be used in the app


# Homepage in the app
def homepage():
    st.set_page_config(
        page_title='Ontology App', 
        page_icon=':bar_chart:', 
        layout='wide', 
        initial_sidebar_state='auto'
    )
    
    st.title("Ontology Management App")
    
    
    
    return None


homepage()

    
