import streamlit as st
import os
from owlready2 import get_ontology
from pyvis.network import Network
from tools.file_handler import get_schema_files
import tempfile

# Directory where schema ontology files are stored
schemas_dir = "./schemas"

st.set_page_config(page_title="Ontology Schema Graph", layout="wide")

st.title("Ontology Schema Graph Visualization")

# List all Schemas in the schemas directory
schema_files = get_schema_files()

if schema_files:
    selected_schema = st.sidebar.selectbox("Select a schema to load", schema_files)
    
    if selected_schema:
        schema_path = os.path.join(schemas_dir, selected_schema)
        onto = get_ontology(schema_path).load()
        st.sidebar.write(f"Schema '{selected_schema}' loaded successfully.")
        
        # Create a Pyvis network
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        
        # Add nodes from ontology
        for cls in onto.classes():
            net.add_node(cls.name, label=cls.name, title=cls.name)
        
        # Add edges for subclasses
        for cls in onto.classes():
            for sub_cls in cls.subclasses():
                net.add_edge(cls.name, sub_cls.name, title="subclass of")
        
        # Add edges for object properties
        for prop in onto.object_properties():
            for domain in prop.domain:
                for range_ in prop.range:
                    net.add_edge(domain.name, range_.name, title=prop.name)
        
        # Add edges for data properties
        for prop in onto.data_properties():
            for domain in prop.domain:
                net.add_node(prop.name, label=prop.name, title=prop.name, shape='box')
                net.add_edge(domain.name, prop.name, title="has data property")
        
        # Generate the network and save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.save_graph(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Display the network in Streamlit
        with open(tmp_file_path, "r") as f:
            html_content = f.read()
            st.components.v1.html(html_content, height=750)
        
        try:
            onto.destroy()
        except:
            pass
            
else:
    st.write("No schemas found in the schemas directory.")
