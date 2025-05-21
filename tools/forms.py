import streamlit as st
from owlready2 import *
from tools import helper
import pandas as pd
import math

# Function to add project data to the ontology
@st.dialog("Create Project")
def create_project_form(schema_path):
    with st.form("create_project_form"):
        project_data = {
            'ProjectID': st.text_input("Project ID"),
            'ProjectName': st.text_input("Project Name"),
            'ProjectOwner': st.text_input("Project Owner"),
            'ProjectLocation': st.text_input("Project Location"),
            'ProjectType': st.text_input("Project Type"),
            'ProjectPhase': st.text_input("Project Phase"),
            'ProjectStartDate': st.date_input("Project Start Date", value=None),
            'ProjectFinishDate': st.date_input("Project Finish Date", value=None),
            'ProjectDuration': st.number_input("Project Duration", min_value=0, step=1, value=None),
            'ProjectBudget': st.number_input("Project Budget", min_value=0.0, step=0.01, value=None),   
            'ProjectStatus': st.text_input("Project Status")
        }
        submitted = st.form_submit_button("Create Project")
        if submitted:
            # helper.add_project(project_data, schema_path)
            st.success("Project added successfully!")
            st.rerun()
            
@st.dialog("Create WBS")
def create_wbs_form(project_path):
    wbs_details = helper.get_wbs_details(project_path)
    wbs_list = [wbs['Id'] for wbs in wbs_details]
    with st.form("create_WBS_form"):
        wbs_data = {
            'Id': st.text_input("WBS ID"),
            'Name': st.text_input("WBS Name"),
            'Description': st.text_input("Description"),
            'ParentWBS': st.selectbox("Parent WBS", wbs_list, index=None)
        }
        submitted = st.form_submit_button("Create WBS")
        if submitted:
            # helper.add_wbs(wbs_data, project_path)
            st.success("WBS added successfully!")
            st.rerun()

@st.dialog("Load WBS from CSV", width="large")
def load_wbs_from_csv_form(project_path):
    wbs_file = st.file_uploader("Upload WBS csv file", type=["csv"])
    if wbs_file is not None:
        wbs_data = pd.read_csv(
            wbs_file,
            dtype={"Id": str, "Name": str, "Description": str, "ParentWBS": str},
            na_filter=False
        )

        wbs_data.reset_index(drop=True, inplace=True)
        wbs_data = st.data_editor(wbs_data, use_container_width=True, disabled=['Id']).to_dict(orient="records")

    # Form for confirming and applying changes
    with st.form("load_wbs_from_csv_form"):
        submitted = st.form_submit_button("Apply WBS Data")
        if submitted and wbs_file is not None:
            for row in wbs_data:
                helper.add_wbs(row, project_path)
            st.success("WBS loaded and updated successfully!")
            st.rerun()
            
@st.dialog("Create Task")
def create_task_form(project_path):
    # Fetch WBS details and task details
    wbs_details = helper.get_wbs_details(project_path)  # Example: [{'Id': 'WBS_1', 'Name': 'Foundation'}, ...]
    wbs_id_to_name = {wbs['Id']: wbs['Name'] for wbs in wbs_details}
    wbs_name_to_id = {v: k for k, v in wbs_id_to_name.items()}  # Reverse mapping
    wbs_list = list(wbs_name_to_id.keys())

    task_details = helper.get_task_details(project_path)  # Example: [{'Id': 'Task_123', 'Name': 'Excavation'}, ...]
    task_id_to_name = {task['Id']: task['Name'] for task in task_details}
    task_name_to_id = {v: k for k, v in task_id_to_name.items()}  # Reverse mapping
    task_list = ["None"] + list(task_name_to_id.keys())

    # Display the form
    with st.form("create_task_form"):
        task_data = {
            'Id': st.text_input("Task ID"),
            'Name': st.text_input("Task Name", value=None),
            'Description': st.text_input("Description", value=None),
            'WBS': st.selectbox("WBS", wbs_list),  # Show WBS names
            'ParentTask': st.selectbox("Parent Task", task_list),  # Show task names
            'Predecessors': st.multiselect("Predecessors", task_list),  # Show task names
            'PlannedDuration': st.number_input("Planned Duration", min_value=0, step=1, value=None),
            'PlannedStart': st.date_input("Planned Start", value=None),
            'PlannedFinish': st.date_input("Planned Finish", value=None),
            'ActualDuration': st.number_input("Actual Duration", min_value=0, step=1, value=None),
            'ActualStart': st.date_input("Actual Start", value=None),
            'ActualFinish': st.date_input("Actual Finish", value=None),
            'RemainingDuration': st.number_input("Remaining Duration", min_value=0, step=1, value=None),
            'AtCompleteDuration': st.number_input("At Complete Duration", min_value=0, step=1, value=None),
            'Resources': st.text_area("Resources (comma-separated)", value=""),
            'Expense': st.number_input("Expense", min_value=0.0, step=0.01, value=None),
            'ExpenseType': st.text_input("Expense Type", value=None),
        }
        submitted = st.form_submit_button("Create Task")
        if submitted:
            # Convert selected names back to IDs for WBS, Parent Task, and Predecessors
            task_data['WBS'] = wbs_name_to_id[task_data['WBS']]
            task_data['ParentTask'] = None if task_data['ParentTask'] == "None" else task_name_to_id[task_data['ParentTask']]
            task_data['Predecessors'] = [task_name_to_id[predecessor] for predecessor in task_data['Predecessors'] if predecessor != "None"]
            task_data['Resources'] = [resource.strip() for resource in task_data['Resources'].split(",") if resource.strip()]
            # Add the task to the ontology
            # st.write(task_data)
            # helper.add_task(task_data, project_path)
            st.success("Task added successfully!")
            st.rerun()
            
@st.dialog("Load Task from CSV", width="large")
def load_task_from_csv_form(project_path):
    task_file = st.file_uploader("Upload Task csv file", type=["csv"])
    if task_file is not None:
        task_data = pd.read_csv(
            task_file,
            dtype={"Id": str, "Name": str, "Description": str, "WBS": str, "ParentTask": str, "Resources": str, "Predecessors": str},
            na_filter=False
        )

        task_data.reset_index(drop=True, inplace=True)
        
        # Convert empty strings or blank values to None
        task_data = task_data.applymap(lambda x: None if x == "" else x)
        
        # Convert date columns to datetime objects
        date_columns = ['PlannedStart', 'PlannedFinish', 'ActualStart', 'ActualFinish']
        for col in date_columns:
            if col in task_data.columns:
                task_data[col] = pd.to_datetime(task_data[col], errors='coerce')
                task_data[col] = task_data[col].dt.date
                task_data[col] = task_data[col].apply(lambda x: None if pd.isna(x) else x)

        # Convert numeric columns to float
        numeric_columns = ['PlannedDuration', 'ActualDuration', 'RemainingDuration', 'AtCompleteDuration', 'BudgetedCost', 'ActualCost', 'RemainingCost', 'AtCompleteCost', 'Expense']
        for col in numeric_columns:
            if col in task_data.columns:
                task_data[col] = task_data[col].apply(lambda x: None if x is None else float(x))

        task_data = st.data_editor(task_data, use_container_width=True, disabled=["Id"]).to_dict(orient="records")

    # Form for confirming and applying changes
    with st.form("load_task_from_csv_form"):
        submitted = st.form_submit_button("Apply Task Data")
        if submitted and task_file is not None:
            for row in task_data:
                # Correctly process the Resources and Predecessors fields
                if 'Resources' in row and isinstance(row['Resources'], str):
                    row['Resources'] = [resource.strip() for resource in row['Resources'].strip("[]").replace("'", "").split(",") if resource.strip()]
                if 'Predecessors' in row and isinstance(row['Predecessors'], str):
                    row['Predecessors'] = [predecessor.strip() for predecessor in row['Predecessors'].strip("[]").replace("'", "").split(",") if predecessor.strip()]
                # st.write(row)
                # helper.add_task(row, project_path)
            st.success("Task loaded and updated successfully!")
            st.rerun()

@st.dialog("Load Resources from CSV", width="large")
def load_resources_from_csv_form(project_path):
    resource_file = st.file_uploader("Upload Resource csv file", type=["csv"])
    if resource_file is not None:
        resource_data = pd.read_csv(
            resource_file,
            dtype={"Task": str, "ResourceItem": str, "ResourceType": str, "ResourceCategory": str, "Description": str},
            na_filter=False
        )

        resource_data.reset_index(drop=True, inplace=True)
        
        # Convert empty strings or blank values to None
        resource_data = resource_data.applymap(lambda x: None if x == "" else x)
        
        # Convert numeric columns to float
        numeric_columns = ['BudgetedUnits', 'ActualUnits', 'RemainingUnits', 'AtCompleteUnits']
        for col in numeric_columns:
            if col in resource_data.columns:
                resource_data[col] = resource_data[col].apply(lambda x: None if x is None else float(x))

        resource_data = st.data_editor(resource_data, use_container_width=True, disabled=["Task"]).to_dict(orient="records")

    # Form for confirming and applying changes
    with st.form("load_resources_from_csv_form"):
        submitted = st.form_submit_button("Apply Resource Data")
        if submitted and resource_file is not None:
            for row in resource_data:
                helper.update_resource_assignments(row, project_path)
            st.success("Resource loaded and updated successfully!")
            st.rerun()

@st.dialog("Filter WBS")
def filter_wbs_form(project_path):
    wbs_details = helper.get_wbs_details(project_path)
    with st.form("filter_wbs_form"):
        filter_criteria = {
            'Id': st.text_input("WBS ID"),
            'Name': st.text_input("WBS Name"),
            'Description': st.text_input("Description"),
            'ParentWBS': st.text_input("Parent WBS ID")
        }
        submitted = st.form_submit_button("Filter WBS")
        if submitted:
            filtered_wbs = helper.filter_data(wbs_details, {k: v for k, v in filter_criteria.items() if v})
            st.write(filtered_wbs)

@st.dialog("Filter Task")
def filter_task_form(project_path):
    task_details = helper.get_task_details(project_path)
    with st.form("filter_task_form"):
        filter_criteria = {
            'Id': st.text_input("Task ID"),
            'Name': st.text_input("Task Name"),
            'Description': st.text_input("Description"),
            'ParentTask': st.text_input("Parent Task ID"),
            'WBS': st.text_input("WBS ID")
        }
        submitted = st.form_submit_button("Filter Task")
        if submitted:
            filtered_tasks = helper.filter_data(task_details, {k: v for k, v in filter_criteria.items() if v})
            st.write(filtered_tasks)


@st.dialog("Create Resource")
def create_resource_form(project_path):
    onto = get_ontology(project_path).load()
    with onto:
        resource_type_list = [r.name for r in onto.ResourceType.instances()]
        resource_category_list = [r.name for r in onto.ConstructionResource.instances()]
    try:
        onto.destroy()
    except:
        pass
    tasks = helper.get_task_details(project_path)
    task_ids = [t['Id'] for t in tasks] if tasks else []
    task_resource_map = {t['Id']: t['ResourceItem'] for t in tasks if t['ResourceItem']}
    task_id_to_name = {task['Id']: task['Name'] for task in tasks}
    task_name_to_id = {v: k for k, v in task_id_to_name.items()}  # Reverse mapping
    task_list = list(task_name_to_id.keys())
    with st.form("create_resource_form"):
        st.write("Fill Resource Details")
        selected_task = st.selectbox("Select Task", task_list)
        resource_type = st.selectbox("Resource Type", resource_type_list)
        resource_category = st.selectbox("Resource Category", resource_category_list)
        description = st.text_area("Description", value=None)
        budgeted_units = st.number_input("Budgeted Units", min_value=0.0, step=1.0, value=None)
        is_primary = st.checkbox("Is Primary Resource")
        


        if st.form_submit_button("Add Resource"):
            new_resource_data = {
                'Task': task_name_to_id[selected_task],
                'ResourceItem': task_resource_map.get(selected_task, ""),
                'Description': description,
                'ResourceType': resource_type,
                'ResourceCategory': resource_category,
                'TrackingTag': None,
                'IsPrimaryResource': is_primary,
                'BudgetedUnits': budgeted_units,
            }
            # helper.update_resource_assignments(new_resource_data, project_path)
            st.success("Resource added successfully!")
            st.rerun()
            
@st.dialog("Load Resources from CSV", width="large")
def load_resources_from_csv_form(project_path):
    resource_file = st.file_uploader("Upload Resource csv file", type=["csv"])
    if resource_file is not None:
        resource_data = pd.read_csv(
            resource_file,
            dtype={"Task": str, "ResourceItem": str, "ResourceType": str, "ResourceCategory": str, "Description": str},
            na_filter=False
        )

        resource_data.reset_index(drop=True, inplace=True)
        
        # Convert empty strings or blank values to None
        resource_data = resource_data.applymap(lambda x: None if x == "" else x)
        
        # Convert numeric columns to float
        numeric_columns = ['BudgetedUnits', 'ActualUnits', 'RemainingUnits', 'AtCompleteUnits']
        for col in numeric_columns:
            if col in resource_data.columns:
                resource_data[col] = resource_data[col].apply(lambda x: None if x is None else float(x))

        resource_data = st.data_editor(resource_data, use_container_width=True, disabled=["Task"]).to_dict(orient="records")

    # Form for confirming and applying changes
    with st.form("load_resources_from_csv_form"):
        submitted = st.form_submit_button("Apply Resource Data")
        if submitted and resource_file is not None:
            for row in resource_data:
                helper.update_resource_assignments(row, project_path)
            st.success("Resource loaded and updated successfully!")
            st.rerun()

@st.dialog("Create Project Resource")
def create_project_resource_form(project_path):
    onto = get_ontology(project_path).load()
    with onto:
        resource_type_list = [cls.__name__ for cls in [onto.EquipmentResource, onto.MaterialResource, onto.LaborResource, onto.UserDefinedResource]]
    try:
        onto.destroy()
    except:
        pass

    with st.form("create_project_resource_form"):
        resource_data = {
            'Id': st.text_input("Resource"),
            'ResourceCode':st.text_input("Resource Code"),
            'Description': st.text_input("Description"),
            "UnitOfMeasure": st.text_input("Measuring Units"),
            'BaseRate_onDate': st.number_input("Base Rate on Date", min_value=0.0, step=0.01, value=None),
            'MaxUnits_per_day': st.number_input("Max Units per Day", min_value=0.0, step=0.01, value=None),
            'ResourceType': st.selectbox("Resource Type", resource_type_list)
        }
        submitted = st.form_submit_button("Create Resource")
        if submitted:
            # Handle None and blank values
            resource_data["ResourceCode"] = resource_data["ResourceCode"] if resource_data["ResourceCode"] else None
            resource_data["UnitOfMeasure"] = resource_data["UnitOfMeasure"] if resource_data["UnitOfMeasure"] else None
            resource_data['Description'] = resource_data['Description'] if resource_data['Description'] else None
            resource_data['BaseRate_onDate'] = resource_data['BaseRate_onDate'] if resource_data['BaseRate_onDate'] is not None and not math.isnan(resource_data['BaseRate_onDate']) else None
            resource_data['MaxUnits_per_day'] = resource_data['MaxUnits_per_day'] if resource_data['MaxUnits_per_day'] is not None and not math.isnan(resource_data['MaxUnits_per_day']) else None
            # helper.add_project_resource(resource_data, project_path)
            st.success("Resource added successfully!")
            st.rerun()

@st.dialog("Filter Project Resources")
def filter_project_resources_form(project_path):
    resources = helper.get_project_resources(project_path)
    with st.form("filter_project_resources_form"):
        filter_criteria = {
            'ResourceType': st.selectbox("Resource Type", ["All"] + list(set([res['ResourceType'] for res in resources])))
        }
        submitted = st.form_submit_button("Filter Resources")
        if submitted:
            filtered_resources = [res for res in resources if filter_criteria['ResourceType'] == "All" or res['ResourceType'] == filter_criteria['ResourceType']]
            st.write(filtered_resources)
            
@st.dialog("Load Project Resources from CSV", width="large")            
def load_project_resources_from_csv(project_path):
    resource_file = st.file_uploader("Upload Project Resource csv file", type=["csv"])
    if resource_file is not None:
        resource_data = pd.read_csv(
            resource_file,
            dtype={"Id": str, "Name": str, "Description": str, "ResourceType": str},
            na_filter=False
        )

        resource_data.reset_index(drop=True, inplace=True)
        
        # Convert empty strings or blank values to None
        resource_data = resource_data.applymap(lambda x: None if x == "" else x)
        
        # Convert numeric columns to float
        numeric_columns = ['BaseRate_onDate', 'MaxUnits_per_day']
        for col in numeric_columns:
            if col in resource_data.columns:
                resource_data[col] = resource_data[col].apply(lambda x: None if x is None else float(x))

        resource_data = st.data_editor(resource_data, use_container_width=True, disabled=["Id"]).to_dict(orient="records")

    with st.form("load_project_resources_from_csv_form"):
        submitted = st.form_submit_button("Apply Project Resource Data")
        if submitted and resource_file is not None:
            for row in resource_data:
                helper.update_project_resource(row, project_path)
            st.success("Project resource data loaded and updated successfully!")
            st.rerun()