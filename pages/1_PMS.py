import streamlit as st
from tools import file_handler
from tools import helper
from tools import forms
from owlready2 import *
import os
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_echarts import st_echarts
from tools.cost_calculations import calculate_costs, calculate_resource_costs, calculate_resource_category_costs, calculate_resource_type_costs

st.set_page_config(page_title="Project Management System", page_icon=":bar_chart:", layout="wide")

# Intialise the functions from the file handler
save_schema_file = file_handler.save_schema_file
save_project_file = file_handler.save_project_file
get_project_files = file_handler.get_project_files

#Intilaise the functions from the ontology helper file
add_wbs = helper.add_wbs
add_task = helper.add_task
update_task = helper.update_task
get_project_details = helper.get_project_details
get_wbs_details = helper.get_wbs_details
update_project = helper.update_project
get_task_details = helper.get_task_details
get_resource_assignments = helper.get_resource_assignments
update_resource_assignments = helper.update_resource_assignments    
get_project_resources = helper.get_project_resources
update_project_resource = helper.update_project_resource 

# Intialise the functions from the forms
create_project_form = forms.create_project_form
create_wbs_form = forms.create_wbs_form
load_wbs_from_csv_form = forms.load_wbs_from_csv_form
create_task_form = forms.create_task_form
load_task_from_csv_form = forms.load_task_from_csv_form
filter_wbs_form = forms.filter_wbs_form
filter_task_form = forms.filter_task_form
create_resource_form = forms.create_resource_form
load_resources_from_csv_form = forms.load_resources_from_csv_form
create_project_resource_form = forms.create_project_resource_form
filter_project_resources_form = forms.filter_project_resources_form
load_project_resources_from_csv = forms.load_project_resources_from_csv


# Directory where project ontology files are stored
projects_dir = "./projects"

def calculate_evm_metrics(task_details):
    evm_metrics = {
        'Planned Value (PV)': 0.0,
        'Earned Value (EV)': 0.0,
        'Actual Cost (AC)': 0.0,
        'Cost Variance (CV)': 0.0,
        'Schedule Variance (SV)': 0.0,
        'Cost Performance Index (CPI)': 0.0,
        'Schedule Performance Index (SPI)': 0.0
    }

    for task in task_details:
        if task['PlannedDuration'] and task['BudgetedCost']:
            evm_metrics['Planned Value (PV)'] += task['BudgetedCost']
        if task['ActualDuration'] and task['ActualCost']:
            evm_metrics['Actual Cost (AC)'] += task['ActualCost']
        if task['ActualDuration'] and task['BudgetedCost']:
            evm_metrics['Earned Value (EV)'] += task['BudgetedCost'] * (task['ActualDuration'] / task['PlannedDuration'])

    evm_metrics['Cost Variance (CV)'] = evm_metrics['Earned Value (EV)'] - evm_metrics['Actual Cost (AC)']
    evm_metrics['Schedule Variance (SV)'] = evm_metrics['Earned Value (EV)'] - evm_metrics['Planned Value (PV)']
    evm_metrics['Cost Performance Index (CPI)'] = evm_metrics['Earned Value (EV)'] / evm_metrics['Actual Cost (AC)'] if evm_metrics['Actual Cost (AC)'] != 0 else 0
    evm_metrics['Schedule Performance Index (SPI)'] = evm_metrics['Earned Value (EV)'] / evm_metrics['Planned Value (PV)'] if evm_metrics['Planned Value (PV)'] != 0 else 0

    return evm_metrics

def project_main():
    # Sidebar
    option = st.sidebar.selectbox("Select Option", ["New Project", "Open Project"])
    
    if option == "New Project":
        project_schema_file = st.sidebar.file_uploader("Upload schema", type=["owl"], key="schema")
        if project_schema_file is not None:
            schema_path = save_schema_file(project_schema_file)
            st.sidebar.success("Project schema loaded successfully.")
        
        schema_files = [f for f in os.listdir("schemas") if f.endswith('.owl')]
        selected_schema = st.sidebar.selectbox("Select a schema to load", schema_files)
        
        if selected_schema:
            schema_path = os.path.join("schemas", selected_schema)

            if st.sidebar.button("Create Project"):
                create_project_form(schema_path)
              
    
    elif option == "Open Project":
        project_file = st.sidebar.file_uploader("Upload Project Ontology file", type=["owl"], key="project", on_change=None)
        if project_file is not None:
            project_path = save_project_file(project_file)
            st.sidebar.success("Project loaded successfully.")
            
    # Page header with custom styling
    st.markdown('<h1 class="dashboard-title">Project Management System</h1>', unsafe_allow_html=True)
    st.write("Welcome to the project Management System")
    
    # List all Projects in the projects directory
    project_files = get_project_files()
    
    if project_files:
        selected_project = st.selectbox("Select a project to load", project_files)
        
        if selected_project:
            project_path = os.path.join(projects_dir, selected_project)
            project_details = get_project_details(project_path)
            wbs_details = get_wbs_details(project_path)
            task_details = get_task_details(project_path)
            resource_data = get_resource_assignments(project_path)
            project_resource_data = get_project_resources(project_path)
            task_costs = calculate_costs(project_path)
            resource_costs = calculate_resource_costs(project_path)
            resource_category_costs = calculate_resource_category_costs(project_path)
            resource_type_costs = calculate_resource_type_costs(project_path)
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Project Details", "📊 WBS Details", "📝 Task Details", "🔧 Resource Details", "💰 Cost Details", "📈 Project Data"])
            
            with tab1:
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.header("Project Details")
                
                # Convert date columns to datetime objects
                for project in project_details:
                    if project.get('ProjectStartDate'):
                        project['ProjectStartDate'] = pd.to_datetime(project['ProjectStartDate'])
                    if project.get('ProjectFinishDate'):
                        project['ProjectFinishDate'] = pd.to_datetime(project['ProjectFinishDate'])
                
                edited_project = st.data_editor(project_details, column_config={
                    "ProjectStartDate": st.column_config.DateColumn("Start Date", disabled=False),
                    "ProjectFinishDate": st.column_config.DateColumn("Finish Date", disabled=False)
                }, disabled=["ProjectID"])
                
                if st.button("Update Project"):
                    date_columns = ['ProjectStartDate', 'ProjectFinishDate']
                    for col in date_columns:
                        if col in edited_project[0].keys():
                            edited_project[0][col] = pd.to_datetime(edited_project[0][col], errors='coerce')
                            if isinstance(edited_project[0][col], pd.Timestamp):
                                edited_project[0][col] = edited_project[0][col].date()
                    update_project(edited_project[0], project_path)
                    st.success("Project updated successfully!")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.header("WBS Details")
                # Add WBS 
                if st.button("Create WBS"):
                    create_wbs_form(project_path)  
                    
                # Display WBS
                st.header("WBS Details")
                wbs_details = get_wbs_details(project_path)
                wbs_list = [wbs['Id'] for wbs in wbs_details]
                edited_wbs = st.data_editor(wbs_details, column_config={
                    "ParentWBS": st.column_config.SelectboxColumn("Parent WBS", options=wbs_list),
                    'Id': 'WBS ID',
                }, disabled=["Id"],use_container_width=False)
                
                if st.button("Update WBS"):
                    for wbs_data in edited_wbs:
                        add_wbs(wbs_data, project_path)
                    st.success("WBS updated successfully!")
                
                if st.button("Load WBS from csv"):
                    load_wbs_from_csv_form(project_path)
                    
                if st.button("Filter WBS"):
                    filter_wbs_form(project_path)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab3:
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.header("Task Details")
                # Add Task
                if st.button("Create Task"):
                    create_task_form(project_path)
                    
                # Display Task
                st.header("Task Details")
                task_details = get_task_details(project_path)
                task_list = [task['Id'] for task in task_details]
                wbs_details = get_wbs_details(project_path)
                wbs_list = [wbs['Id'] for wbs in wbs_details]
                
                # Checkboxes to hide/unhide certain sets of information
                with st.popover("Filter items"):
                    show_planned_info = st.checkbox("Show Planned Information", value=True)
                    show_progress_info = st.checkbox("Show Progress Information", value=True)
                    show_resource_info = st.checkbox("Show Resource Information", value=True)
                    show_cost_info = st.checkbox("Show Cost Information", value=True)
                    selected_wbs = st.multiselect("Select WBS to display", wbs_list, default=None)
                
                # Filter columns based on checkboxes
                columns_to_display = ['Id', 'Name', 'Description', 'ParentTask', 'WBS', 'Predecessors']
                if show_planned_info:
                    columns_to_display += ['TaskSchedule','PlannedDuration', 'PlannedStart', 'PlannedFinish']
                if show_progress_info:
                    columns_to_display += ['TaskSchedule','ActualDuration', 'ActualStart', 'ActualFinish', 'RemainingDuration', 'AtCompleteDuration']
                if show_resource_info:
                    columns_to_display += ['ResourceItem','Resources']
                if show_cost_info:
                    columns_to_display += ['CostItem','BudgetedCost', 'ActualCost', 'RemainingCost', 'AtCompleteCost', 'Expense', 'ExpenseType']
                
                # If no WBS is selected, display all tasks
                if not selected_wbs:
                    filtered_task_details = [
                        {k: v for k, v in task.items() if k in columns_to_display} 
                        for task in task_details
                    ]
                else:
                    filtered_task_details = [
                        {k: v for k, v in task.items() if k in columns_to_display} 
                        for task in task_details 
                        if task['WBS'] in selected_wbs
                    ]
                
                # Convert date columns to datetime objects
                for task in filtered_task_details:
                    if task.get('ActualStart'):
                        task['ActualStart'] = pd.to_datetime(task['ActualStart'])
                    if task.get('ActualFinish'):
                        task['ActualFinish'] = pd.to_datetime(task['ActualFinish'])
                    if task.get('PlannedStart'):
                        task['PlannedStart'] = pd.to_datetime(task['PlannedStart'])
                    if task.get('PlannedFinish'):
                        task['PlannedFinish'] = pd.to_datetime(task['PlannedFinish'])
                
                edited_task = st.data_editor(filtered_task_details, column_config={
                    "ParentTask": st.column_config.SelectboxColumn("Parent Task", options=task_list),
                    "WBS": st.column_config.SelectboxColumn("WBS", options=wbs_list),
                    "Predecessors": st.column_config.TextColumn("Predecessors"),
                    'Id': 'Task ID',
                    "PlannedStart": st.column_config.DateColumn("Planned Start", disabled=False),
                    "PlannedFinish": st.column_config.DateColumn("Planned Finish", disabled=False),
                    "ActualStart": st.column_config.DateColumn("Actual Start", disabled=False),
                    "ActualFinish": st.column_config.DateColumn("Actual Finish", disabled=False),
                }, disabled=["Id","TaskSchedule","ResourceItem","CostItem", "BudgetedCost","ActualCost", "RemainingCost", "AtCompleteCost"],use_container_width=False)
                
                if st.button("Update Task"):
                    for task_data in edited_task:
                        # Correctly process the Resources and Predecessors fields
                        if 'Resources' in task_data and isinstance(task_data['Resources'], str):
                            task_data['Resources'] = [resource.strip() for resource in task_data['Resources'].strip("[]").replace("'", "").split(",") if resource.strip()]
                        if 'Predecessors' in task_data and isinstance(task_data['Predecessors'], str):
                            task_data['Predecessors'] = [predecessor.strip() for predecessor in task_data['Predecessors'].strip("[]").replace("'", "").split(",") if predecessor.strip()]
                        
                        # Convert date columns to datetime.date objects
                        date_columns = ['PlannedStart', 'PlannedFinish', 'ActualStart', 'ActualFinish']
                        for col in date_columns:
                            if col in task_data.keys():
                                task_data[col] = pd.to_datetime(task_data[col], errors='coerce')
                                if isinstance(task_data[col], pd.Timestamp):
                                    task_data[col] = task_data[col].date()
                        
                        update_task(task_data, project_path)
                    st.success("Task updated successfully!")
                if st.button("Load Task from csv"):
                    load_task_from_csv_form(project_path)
                    
                if st.button("Filter Task"):
                    filter_task_form(project_path)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab4:
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.header("Resource Details")
                if st.button("Assign Resource"):
                    create_resource_form(project_path)

                onto = get_ontology(project_path).load()
                resource_type_list = [r.name for r in onto.ResourceType.instances()]
                resource_type_class_list = [cls.__name__ for cls in [onto.EquipmentResource, onto.MaterialResource, onto.LaborResource, onto.UserDefinedResource]]
                resource_category_list = [r.name for r in onto.ConstructionResource.instances()]
                try:
                    onto.destroy()
                except:
                    pass

                resource_data = get_resource_assignments(project_path)
                edited_resources = st.data_editor(
                    resource_data,
                    column_config={
                        "Task": st.column_config.TextColumn("Task", disabled=True),
                        "ResourceItem": st.column_config.TextColumn("Resource Item", disabled=True),
                        "Resource": "Resource ID",
                        "Name": "Resource Name",
                        "Description": "Description",
                        "ResourceType": st.column_config.SelectboxColumn("Resource Type", options=resource_type_list),
                        "ResourceCategory": st.column_config.SelectboxColumn("Resource Category", options=resource_category_list),
                        "TrackingTag": "Tracking Tag",
                        "IsPrimaryResource": st.column_config.CheckboxColumn("Is Primary Resource"),
                        "BudgetedUnits": st.column_config.NumberColumn("Budgeted Units"),
                        "ActualUnits": st.column_config.NumberColumn("Actual Units"),
                        "RemainingUnits": st.column_config.NumberColumn("Remaining Units"),
                        "AtCompleteUnits": st.column_config.NumberColumn("At Complete Units"),
                    },
                    use_container_width=True
                )
                if st.button("Update"):
                    for resource_data in edited_resources:
                        update_resource_assignments(resource_data, project_path)
                    st.success("Resource data updated successfully!")
                    st.rerun()
                        
                if st.button("Assign from csv"):
                    load_resources_from_csv_form(project_path)
                st.header("Project-Level Resource Details")
                if st.button("Create Project Resource"):
                    create_project_resource_form(project_path)

                project_resource_data = get_project_resources(project_path)
                
                # Checkboxes to filter project resources by Resource Type
                with st.popover("Filter items"):
                    selected_resource_types = {resource_type: st.checkbox(resource_type, value=True) for resource_type in resource_type_class_list}
                
                filtered_project_resources = [
                    resource for resource in project_resource_data 
                    if selected_resource_types[resource['ResourceType']]
                ]
                
                edited_project_resources = st.data_editor(
                    filtered_project_resources,
                    column_config={
                        "Id": st.column_config.TextColumn("Resource", disabled=True),
                        "Description": "Description",
                        "BaseRate_onDate": st.column_config.NumberColumn("Base Rate on Date"),
                        "MaxUnits_per_day": st.column_config.NumberColumn("Max Units per Day"),
                        "ResourceType": st.column_config.TextColumn("Resource Type", disabled=True)
                    },
                    use_container_width=True
                )
                if st.button("Update Project Resource"):
                    for resource_data in edited_project_resources:
                        update_project_resource(resource_data, project_path)
                    st.success("Project resource data updated successfully!")
                        
                if st.button("Load Project Resource from csv"):
                    load_project_resources_from_csv(project_path)
                    
                if st.button("Filter Project Resource"):
                    filter_project_resources_form(project_path)
                st.markdown('</div>', unsafe_allow_html=True)
                    
            with tab5:
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.header("Cost Details")
                task_details = get_task_details(project_path)
                task_list = [task['Id'] for task in task_details]
                
                # Calculate costs
                task_costs = calculate_costs(project_path)
                task_cost_map = {cost['TaskId']: cost for cost in task_costs}
                
                # Filter columns to display only cost-related data
                cost_columns_to_display = ['Id', 'Name', 'CostItem', 'BudgetedCost', 'ActualCost', 'RemainingCost', 'AtCompleteCost']
                
                filtered_cost_details = [
                    {k: v for k, v in task.items() if k in cost_columns_to_display} 
                    for task in task_details
                ]
                
                # Update cost details with calculated costs
                for task in filtered_cost_details:
                    if task['Id'] in task_cost_map:
                        task.update(task_cost_map[task['Id']])
                        
                st.dataframe(filtered_cost_details)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Resource Budget Costs
                    resource_costs = calculate_resource_costs(project_path)
                    st.header("Budgeted Costs Breakdown")
                    st.dataframe(resource_costs)
                with col2:
                    # Resource Category Costs
                    resource_category_costs = calculate_resource_category_costs(project_path)
                    st.header("Resource Category Cost Share")
                    st.dataframe(pd.DataFrame(list(resource_category_costs.items()), columns=['ResourceCategory', 'TotalCost']))
                with col3:
                    # Resource Type Costs
                    resource_type_costs = calculate_resource_type_costs(project_path)
                    st.header("Resource Type Cost Share")
                    resource_type_df = pd.DataFrame(list(resource_type_costs.items()), columns=['ResourceType', 'TotalCost'])
                    st.write(resource_type_df)

              
            with tab6:
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.header("All Project Details")
                st.subheader("Project Details")
                project_df = pd.DataFrame(project_details)
                st.write(project_df)
                
                st.subheader("WBS Details")
                wbs_df = pd.DataFrame(wbs_details)
                st.write(wbs_df)
                
                st.subheader("Task Details")
                task_df = pd.DataFrame(task_details)
                st.write(task_df)
                
                # st.subheader("Resource Details")
                # resource_df = pd.DataFrame(resource_data)
                # st.write(resource_df)
                
                st.subheader("Cost Details")
                cost_df = pd.DataFrame(task_costs)
                st.write(cost_df)
                
                st.subheader("Project Resource Details")
                project_resource_df = pd.DataFrame(project_resource_data)
                st.write(project_resource_df)
                
                
               
                    
                    
project_main()