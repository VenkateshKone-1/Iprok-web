import streamlit as st
from owlready2 import *
import pandas as pd
import os
import math
import warnings
warnings.filterwarnings("ignore")

project_dir = "projects"
schema_dir = "schemas"
# Function to add project data to the ontology

def add_project(data, schema_path):
    
    try:
        onto = get_ontology(schema_path).load()
    except Exception as e:
        st.error(f"Failed to load ontology from {schema_path}: {e}")
        return
    
    with onto:
        try:
            project = onto.Project(data['ProjectID'])
            project.ProjectName = data['ProjectName']
            project.ProjectOwner = data['ProjectOwner']
            project.ProjectLocation = data['ProjectLocation']
            project.ProjectType = data['ProjectType']
            project.ProjectID = data['ProjectID']
            project.ProjectStartDate = data['ProjectStartDate']
            project.ProjectFinishDate = data['ProjectFinishDate']
            project.ProjectStatus = data['ProjectStatus']
            project.ProjectDuration = data['ProjectDuration']
            project.ProjectBudget = data['ProjectBudget']
            
        except Exception as e:
            st.error(f"Failed to create project in ontology: {e}")
            return
    
    # Create a directory for project files if it doesn't exist
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    # Save the ontology file with the Project ID
    file_path = os.path.join(project_dir, f"{data['ProjectID']}.owl")
    try:
        onto.save(file=file_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")
             
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

def update_project(data, project_path):
    onto = get_ontology(project_path).load()
    with onto:
        try:
            project = onto.Project(data['ProjectID'])
            project.ProjectName = data['ProjectName']
            project.ProjectOwner = data['ProjectOwner']
            project.ProjectLocation = data['ProjectLocation']
            project.ProjectType = data['ProjectType']
            project.ProjectStartDate = data['ProjectStartDate']
            project.ProjectFinishDate = data['ProjectFinishDate']
            project.ProjectStatus = data['ProjectStatus']
            project.ProjectDuration = data['ProjectDuration']
            project.ProjectBudget = data['ProjectBudget']
        except Exception as e:
            st.error(f"Failed to update project in ontology: {e}")
            return
    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")

def add_wbs(data, project_path):
    onto = get_ontology(project_path).load()

    with onto:
        try:
            wbs = onto.WBS(data['Id'])
            wbs.Id = data['Id']
            wbs.Name = data['Name'] if data['Name'] else None
            wbs.Description = data['Description'] if data['Description'] else None
            project = onto.Project.instances()[0]
            project.hasWBS.append(wbs)
            wbs.isSubWBSOf = onto.WBS(data['ParentWBS']) if data['ParentWBS'] else None
        except Exception as e:
            st.error(f"Failed to create WBS in ontology: {e}")
            return
    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")
        
def get_wbs_details(project_path):
    onto = get_ontology(project_path).load()
    all_wbs = []
    for wbs in onto.WBS.direct_instances():
        wbs_data = {
            'Id': wbs.Id,
            'Name': wbs.Name,
            'Description': wbs.Description,
            'ParentWBS': wbs.isSubWBSOf.Id if wbs.isSubWBSOf else None,
            'Tasks': [task.Id for task in wbs.hasTask] if wbs.hasTask else None
        }
        all_wbs.append(wbs_data)
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")
    return all_wbs

def add_task(data, project_path):
    onto = get_ontology(project_path).load()

    def sanitize(value):
        return None if pd.isna(value) else value

    with onto:
        try:
            # Ensure the ontology classes are correctly defined
            if not hasattr(onto, 'Task') or not hasattr(onto, 'TaskSchedule') or not hasattr(onto, 'ResourceItem') or not hasattr(onto, 'CostItem'):
                st.error("Ontology does not have the required classes defined.")
                return

            task = onto.Task(data['Id'])
            task.Id = data['Id']
            task.Name = data.get('Name')
            task.Description = data.get('Description')
            if 'ParentTask' in data and data['ParentTask']:
                task.isSubTaskOf = onto.Task(data['ParentTask'])
            if 'WBS' in data and data['WBS']:
                task.isTaskOf = onto.WBS(data['WBS'])

            # Assign Task Schedule with prefix TS+TaskID
            task_schedule = onto.TaskSchedule(f"TS_{data['Id']}")
            task_schedule.Id = f"TS_{data['Id']}"
            task.hasTaskSchedule = task_schedule
            task_schedule.PlannedDuration = sanitize(data.get('PlannedDuration'))
            task_schedule.PlannedStart = sanitize(data.get('PlannedStart'))
            task_schedule.PlannedFinish = sanitize(data.get('PlannedFinish'))
            task_schedule.ActualDuration = sanitize(data.get('ActualDuration'))
            task_schedule.ActualStart = sanitize(data.get('ActualStart'))
            task_schedule.ActualFinish = sanitize(data.get('ActualFinish'))
            task_schedule.RemainingDuration = sanitize(data.get('RemainingDuration'))
            task_schedule.AtCompleteDuration = sanitize(data.get('AtCompleteDuration'))

            # Assign Resource Item with prefix RI+TaskID
            resource_item = onto.ResourceItem(f"RI_{data['Id']}")
            resource_item.Id = f"RI_{data['Id']}"
            task.hasResourcesItem = resource_item
            if 'Resources' in data and data['Resources']:
                resource_item.hasResources = [onto.Resource(resource) for resource in data['Resources']]

            # Assign Predecessors
            if 'Predecessors' in data and data['Predecessors']:
                task.hasPredecessors = [onto.Task(predecessor) for predecessor in data['Predecessors']]

            # Assign Cost Item with prefix CI+TaskID
            cost_item = onto.CostItem(f"CI_{data['Id']}")
            cost_item.Id = f"CI_{data['Id']}"
            task.hasCostItem = cost_item
            cost_item.BudgetedCost = sanitize(data.get('BudgetedCost'))
            cost_item.ActualCost = sanitize(data.get('ActualCost'))
            cost_item.RemainingCost = sanitize(data.get('RemainingCost'))
            cost_item.AtCompleteCost = sanitize(data.get('AtCompleteCost'))
            cost_item.Expense = data.get('Expense')
            cost_item.ExpenseType = data.get('ExpenseType')
    
        except Exception as e:
            st.error(f"Failed to create Task in ontology: {e}")
            return
    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")

def sanitize(value, default=None):
    return default if pd.isna(value) else value

def update_task(data, project_path):
    onto = get_ontology(project_path).load()

    with onto:
        try:
            task = onto.Task(data['Id'])
            task.Id = data['Id']
            if 'Name' in data:
                task.Name = data['Name']
            if 'Description' in data:
                task.Description = data['Description']
            if 'ParentTask' in data and data['ParentTask']:
                task.isSubTaskOf = onto.Task(data['ParentTask'])
            if 'WBS' in data and data['WBS']:
                task.isTaskOf = onto.WBS(data['WBS'])

            # Update Task Schedule
            task_schedule = task.hasTaskSchedule
            if 'PlannedDuration' in data:
                task_schedule.PlannedDuration = sanitize(data['PlannedDuration'], task_schedule.PlannedDuration)
            if 'PlannedStart' in data:
                task_schedule.PlannedStart = sanitize(data['PlannedStart'], task_schedule.PlannedStart)
            if 'PlannedFinish' in data:
                task_schedule.PlannedFinish = sanitize(data['PlannedFinish'], task_schedule.PlannedFinish)
            if 'ActualDuration' in data:
                task_schedule.ActualDuration = sanitize(data['ActualDuration'], task_schedule.ActualDuration)
            if 'ActualStart' in data:
                task_schedule.ActualStart = sanitize(data['ActualStart'], task_schedule.ActualStart)
            if 'ActualFinish' in data:
                task_schedule.ActualFinish = sanitize(data['ActualFinish'], task_schedule.ActualFinish)
            if 'RemainingDuration' in data:
                task_schedule.RemainingDuration = sanitize(data['RemainingDuration'], task_schedule.RemainingDuration)
            if 'AtCompleteDuration' in data:
                task_schedule.AtCompleteDuration = sanitize(data['AtCompleteDuration'], task_schedule.AtCompleteDuration)

            # Update Resource Item
            resource_item = task.hasResourcesItem
            if 'Resources' in data and data['Resources']:
                resource_item.hasResources = [onto.Resource(resource) for resource in data['Resources']]

            # Update Predecessors
            if 'Predecessors' in data and data['Predecessors']:
                task.hasPredecessors = [onto.Task(predecessor) for predecessor in data['Predecessors']]

            # Update Cost Item
            cost_item = task.hasCostItem
            if 'BudgetedCost' in data:
                cost_item.BudgetedCost = sanitize(data['BudgetedCost'], cost_item.BudgetedCost)
            if 'ActualCost' in data:
                cost_item.ActualCost = sanitize(data['ActualCost'], cost_item.ActualCost)
            if 'RemainingCost' in data:
                cost_item.RemainingCost = sanitize(data['RemainingCost'], cost_item.RemainingCost)
            if 'AtCompleteCost' in data:
                cost_item.AtCompleteCost = sanitize(data['AtCompleteCost'], cost_item.AtCompleteCost)
            if 'Expense' in data:
                cost_item.Expense = sanitize(data['Expense'], cost_item.Expense)
            if 'ExpenseType' in data:
                cost_item.ExpenseType = sanitize(data['ExpenseType'], cost_item.ExpenseType)
    
        except Exception as e:
            st.error(f"Failed to update Task in ontology: {e}")
            return
    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")

def get_task_details(project_path):
    onto = get_ontology(project_path).load()
    tasks = onto.Task.instances()
    task_details = []
    for task in tasks:
        task_schedule = task.hasTaskSchedule
        resource_item = task.hasResourcesItem
        task_resources = resource_item.hasResources if resource_item else None
        task_cost = task.hasCostItem
        task_data = {
            'Id': task.Id if task.Id else None,
            'Name': task.Name if task.Name else None,
            'Description': task.Description if task.Description else None,
            'ParentTask': task.isSubTaskOf.Id if task.isSubTaskOf else None,
            'WBS': task.isTaskOf.Id if task.isTaskOf else None,
            'Predecessors': [predecessor.Id for predecessor in task.hasPredecessors] if task.hasPredecessors else None,
            # Schedule Information
            'TaskSchedule': task_schedule.Id if task_schedule else None,
            'PlannedDuration': task_schedule.PlannedDuration if task_schedule else None,
            'PlannedStart': task_schedule.PlannedStart if task_schedule else None,
            'PlannedFinish': task_schedule.PlannedFinish if task_schedule else None,
            'ActualDuration': task_schedule.ActualDuration if task_schedule else None,
            'ActualStart': task_schedule.ActualStart if task_schedule else None,
            'ActualFinish': task_schedule.ActualFinish if task_schedule else None,
            'RemainingDuration': task_schedule.RemainingDuration if task_schedule else None,
            'AtCompleteDuration': task_schedule.AtCompleteDuration if task_schedule else None,
            # Resource Information
            'ResourceItem': resource_item.Id if resource_item else None,
            'Resources': [resource.name for resource in task_resources] if task_resources else None,
            # Cost Information
            'CostItem': task_cost.Id if task_cost else None,
            'BudgetedCost': task_cost.BudgetedCost if task_cost else None,
            'ActualCost': task_cost.ActualCost if task_cost else None,
            'RemainingCost': task_cost.RemainingCost if task_cost else None,
            'AtCompleteCost': task_cost.AtCompleteCost if task_cost else None,
            'Expense': task_cost.Expense if task_cost else None,
            'ExpenseType': task_cost.ExpenseType if task_cost else None,
            
        }
        task_details.append(task_data)
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")
    return task_details

def filter_data(data, filters):
    filtered_data = []
    for item in data:
        match = True
        for key, value in filters.items():
            if key in item and item[key] != value:
                match = False
                break
        if match:
            filtered_data.append(item)
    return filtered_data

def get_resource_assignments(project_path):
    onto = get_ontology(project_path).load()
    assignments = []
    try:
        for t in onto.Task.instances():
            if t.hasResourcesItem:
                r_item = t.hasResourcesItem
                for r in r_item.hasResources:
                    assignments.append({
                        'Task': t.Id,
                        'ResourceItem': r_item.Id,
                        'Resource': r.Id,
                        'Description': r.Description if hasattr(r, 'Description') else None,
                        'ResourceType': r.hasResourceType.name if r.hasResourceType else None,
                        'ResourceCategory': r.hasResourceCategory.name if r.hasResourceCategory else None,
                        'TrackingTag': r.hasTrackingTag.name if r.hasTrackingTag else None,
                        'IsPrimaryResource': r.IsPrimaryResource if hasattr(r, 'IsPrimaryResource') else False,
                        'BudgetedUnits': r.BudgetedUnits if hasattr(r, 'BudgetedUnits') else None,
                        'ActualUnits': r.ActualUnits if hasattr(r, 'ActualUnits') else None,
                        'RemainingUnits': r.RemainingUnits if hasattr(r, 'RemainingUnits') else None,
                        'AtCompleteUnits': r.AtCompleteUnits if hasattr(r, 'AtCompleteUnits') else None
                    })
    except Exception as e:
        st.warning(f"Failed to retrieve resource assignments: {e}")
    finally:
        try:
            onto.destroy()
        except:
            pass
    return assignments



def update_resource_assignments(data, project_path):
    onto = get_ontology(project_path).load()
    with onto:
        try:
            task = onto.Task(data['Task'])
            if not task.hasResourcesItem:
                r_item = onto.ResourceItem(f"RI_{data['Task']}")
                task.hasResourcesItem = r_item
            else:
                r_item = task.hasResourcesItem
            resource = onto.Resource(f"{data['ResourceCategory']}_{data['Task']}")
            r_item.hasResources.append(resource)
            resource.Id = f"{data['ResourceCategory']}_{data['Task']}"
            if data.get('Description'):
                resource.Description = data['Description']
            if data.get('IsPrimaryResource') is not None:
                resource.IsPrimaryResource = data['IsPrimaryResource']
            if data.get('BudgetedUnits') is not None and not math.isnan(data['BudgetedUnits']):
                resource.BudgetedUnits = float(data['BudgetedUnits'])
            if data.get('ActualUnits') is not None and not math.isnan(data['ActualUnits']):
                resource.ActualUnits = float(data['ActualUnits'])
            if data.get('RemainingUnits') is not None and not math.isnan(data['RemainingUnits']):
                resource.RemainingUnits = float(data['RemainingUnits'])
            if data.get('AtCompleteUnits') is not None and not math.isnan(data['AtCompleteUnits']):
                resource.AtCompleteUnits = float(data['AtCompleteUnits'])
            if data.get('ResourceType'):
                res_type = onto.ResourceType(data['ResourceType'])
                resource.hasResourceType = res_type
            if data.get('ResourceCategory'):
                res_category = onto.search_one(iri=f"*{data['ResourceCategory']}")
                resource.hasResourceCategory = res_category

            # Save the updated ontology
            onto.save(project_path, format="rdfxml")
        except Exception as e:
            st.error(f"Failed to update resource data: {e}")
        finally:
            try:
                onto.destroy()
            except Exception as e:
                st.warning(f"Failed to destroy ontology: {e}")

# Resource Inventory Management

def add_project_resource(data, project_path):
    onto = get_ontology(project_path).load()
    with onto:
        try:
            resource_class = getattr(onto, data['ResourceType'])
            resource = resource_class(data['Id'])
            resource.Id = data['Id']
            resource.Name = data['Id']
            resource.ResorceCode = data['ResourceCode']
            resource.UnitOfMeasure = data['UnitOfMeasure']
            resource.Description = data['Description']
            resource.BaseRate_onDate = data['BaseRate_onDate']
            resource.MaxUnits_per_day = data['MaxUnits_per_day']
        except Exception as e:
            st.error(f"Failed to create resource in ontology: {e}")
            return
    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")

def get_project_resources(project_path):
    onto = get_ontology(project_path).load()
    resources = []
    for resource_class in [onto.EquipmentResource, onto.MaterialResource, onto.LaborResource, onto.UserDefinedResource]:
        for resource in resource_class.instances():
            resource_data = {
                'ResourceCode': resource.ResourceCode,
                'Id': resource.name,
                'Description': resource.Description,
                'UnitOfMeasure': resource.UnitOfMeasure,
                'BaseRate_onDate': resource.BaseRate_onDate,
                'MaxUnits_per_day': resource.MaxUnits_per_day,
                'ResourceType': resource.__class__.__name__
            }
            resources.append(resource_data)
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")
    return resources

def update_project_resource(data, project_path):
    onto = get_ontology(project_path).load()
    with onto:
        try:
            resource_class = getattr(onto, data['ResourceType'])
            resource = resource_class(data['Id'])
            resource.Id = data['Id']
            if data.get('Id') not in [None, "", "None"]:
                resource.Name = data['Id']
            if data.get('ResourceCode') not in [None, "", "None"]:
                resource.ResorceCode = data['ResourceCode']
            if data.get('UnitOfMeasure') not in [None, "", "None"]:
                resource.UnitOfMeasure = data['UnitOfMeasure']
            if data.get('Description') not in [None, "", "None"] :
                resource.Description = data['Description']
            if data.get('BaseRate_onDate') not in [None, "", "None"] and not math.isnan(data['BaseRate_onDate']):
                resource.BaseRate_onDate = float(data['BaseRate_onDate'])
            if data.get('MaxUnits_per_day') not in [None, "", "None"] and not math.isnan(data['MaxUnits_per_day']):
                resource.MaxUnits_per_day = float(data['MaxUnits_per_day'])
        except Exception as e:
            st.error(f"Failed to update project resource in ontology: {e}")
            return
    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        st.error(f"Failed to save ontology file: {e}")
    
    try:
        onto.destroy()
    except Exception as e:
        st.warning(f"Failed to destroy ontology: {e}")

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



