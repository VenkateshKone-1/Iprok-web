import streamlit as st
from owlready2 import *
import os

project_dir = "projects"

# Function to save the schema file
def save_schema_file(uploaded_file):
    schema_dir = "schemas"
    if not os.path.exists(schema_dir):
        os.makedirs(schema_dir)
    
    schema_path = os.path.join(schema_dir, uploaded_file.name)
    with open(schema_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    
    return schema_path

def save_project_file(uploaded_file):
    project_dir = "projects"
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    project_path = os.path.join(project_dir, uploaded_file.name)
    with open(project_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    
    return project_path


def get_project_files():
    return [f for f in os.listdir(project_dir) if f.endswith('.owl')]

def get_schema_files():
    schema_dir = "schemas"
    return [f for f in os.listdir(schema_dir) if f.endswith('.owl')]