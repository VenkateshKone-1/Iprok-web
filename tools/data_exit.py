import streamlit as st
from owlready2 import *
import os
import math
import warnings
warnings.filterwarnings("ignore")

project_dir = "projects"
schema_dir = "schemas"

def get_project_details(project_path):
    onto = get_ontology(project_path).load()
    project = onto.Project.instances()[0]
    project_data = [ {
        'ProjectID': project.ProjectID,
        'ProjectName': project.ProjectName,
        'ProjectOwner': project.ProjectOwner,
        'ProjectLocation': project.ProjectLocation,
        'ProjectType': project.ProjectType,
        'ProjectStartDate': project.ProjectStartDate,
        'ProjectFinishDate': project.ProjectFinishDate,
        'ProjectStatus': project.ProjectStatus,
        'ProjectDuration': project.ProjectDuration,
        'ProjectBudget': project.ProjectBudget
    } ]
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")
    return project_data

