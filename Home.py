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

    # Main Title and Subtitle
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="color:#2E86C1;">Integrated Project Knowledge (IproK) Ontology Management App</h1>
            <h3 style="color:#117A65;">Efficient Project Data Management with IproK-Ontology</h3>
        </div>
        """, unsafe_allow_html=True
    )

    # Author Details
    st.markdown(
        """
        <div style="background-color:#2E86C1; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
            <b>Kone Venkatesh</b> <br>
            Research Scholar <br>
            National Institute of Technology Karnataka, Surathkal <br>
            <a href="mailto:konevenkatesh92@gmail.com">konevenkatesh92@gmail.com</a> <br>
            <a href="https://www.linkedin.com/in/venkatesh-kone-66149a13b/" target="_blank">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True
    )

    # Achievements & Introduction
    st.markdown(
        """
        <div style="padding: 1rem 0;">
            <h4>💡 <span style="color:#2874A6;">Introducing <b>IproK-Ontology</b></span></h4>
            <ul>
                <li>A unified <b>.owl</b> file designed to integrate project knowledge seamlessly.</li>
                <li>Built using <b>Owlready2</b>, enabling <i>ontology-oriented programming</i> (think of it as OOP for ontologies).</li>
                <li>Acts as a knowledge base—extract data via SPARQL queries or Python libraries, and serialize it into various formats.</li>
                <li>Supports dynamic updates and integration of external data sources through the web app.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True
    )

    # Features
    st.markdown(
        """
        <div style="padding: 1rem 0;">
            <h4>🔧 <span style="color:#2874A6;">Web App Features</span></h4>
            <ul>
                <li>📁 Create projects under a defined schema.</li>
                <li>🔗 Add WBS (Work Breakdown Structure) and task-related values through an intuitive UI.</li>
                <li>📄 Load & update values using CSV files.</li>
                <li>🛠️ Assign project resources to tasks.</li>
                <li>💰 Automated cost calculations.</li>
                <li>📊 Interactive project dashboard.</li>
                <li>🌐 Schema visualization.</li>
                <li>🔍 Built with:</b> Streamlit for UI <a href="https://owlready2.readthedocs.io/en/latest/" target="_blank">Owlready2</a> for ontology development.</li>
    
        </div>
        """, unsafe_allow_html=True
    )

    # Future Plans
    st.markdown(
        """
        <div style="padding: 1rem 0;">
            <h4>🚀 <span style="color:#2874A6;">Future Plans</span></h4>
            <ul>
                <li>📈 Extend the schema to include risk and quality domains.</li>
                <li>🏗️ BIM Model Integration (via BIMOnto, one of my ongoing projects).</li>
                <li>🤖 Apply ML models for predictive insights.</li>
                <li>🤖 AI integration (using LLMs) to interact with project data.</li>
                <li>📑 Enable automated report generation.</li>
            </ul>
            <p>
                <b>🔍 Looking Forward to Your Thoughts and Feedback!</b>
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    st.info("Navigate using the sidebar to explore features and manage your project data with IproK-Ontology.")

    return None

homepage()


