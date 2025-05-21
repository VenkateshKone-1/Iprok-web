import streamlit as st
import os
from tools.file_handler import get_project_files
from streamlit_elements import elements, mui, html
import pandas as pd
from tools.helper import get_project_details, get_wbs_details, get_task_details, get_resource_assignments, get_project_resources
from owlready2 import *
import plotly.express as px
from streamlit_echarts import st_echarts
from tools.cost_calculations import calculate_costs, calculate_resource_costs, calculate_resource_category_costs, calculate_resource_type_costs

# Must be the first Streamlit command
st.set_page_config(
    page_title="Construction Project Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directory where project ontology files are stored
projects_dir = "./projects"

# Enhanced custom styling
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background-color: #1a1a1a;
        color: white;
    }
    
    /* Title Styling */
    .dashboard-title {
        text-align: center;
        color: white;
        padding: 20px 0;
        font-size: 2.5em;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Metric Container Styles */
    .metric-container {
        background-color: #363636;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #4d4d4d;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        text-align: center;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Metric Label Styling */
    .metric-label {
        font-size: 1.1em;
        color: #e0e0e0;
        margin-bottom: 10px;
        font-weight: 500;
    }
    
    /* Metric Value Styling */
    .metric-value {
        font-size: 1.8em;
        color: #ffffff;
        font-weight: 600;
        margin-top: 5px;
    }
    
    /* Override Streamlit's default metric styling */
    [data-testid="stMetricLabel"] {
        font-size: 1.1em !important;
        color: #e0e0e0 !important;
        font-weight: 500 !important;
        text-align: center !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8em !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        text-align: center !important;
    }

    /* Container Styles */
    .dashboard-container {
        background-color: #2d2d2d;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 15px 0px;
        border: 1px solid #3d3d3d;
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #2d2d2d;
        padding: 10px 10px 0 10px;
        border-radius: 10px 10px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #363636;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #4d4d4d;
    }
    
    /* Chart Container Styles */
    .chart-container {
        background-color: #363636;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #4d4d4d;
    }
    
    /* Header Styles */
    h1, h2, h3 {
        color: white !important;
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background-color: #363636;
        color: white !important;
    }
    
    /* Metric Text Colors */
    .css-1wivap2 {     /* Metric label */
        color: #ffffff90;
    }
    .css-1w22q7d {     /* Metric value */
        color: white;
    }
    
    /* Plot background colors */
    .js-plotly-plot .plotly .bg {
        fill: #363636;
    }
    </style>
    """, unsafe_allow_html=True)

# Page header with custom styling
st.markdown('<h1 class="dashboard-title">Construction Project Dashboard</h1>', unsafe_allow_html=True)

# List all Projects in the projects directory
project_files = get_project_files()

if project_files:
    selected_project = st.sidebar.selectbox("Select a project to load", project_files)
    
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
        
        # Project Summary Cards
        st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        # Helper function to safely calculate project duration
        def calculate_project_duration(task_details):
            try:
                if not task_details:
                    return 0
                
                valid_tasks = [task for task in task_details 
                             if task.get('PlannedStart') and task.get('PlannedFinish')]
                
                if not valid_tasks:
                    return 0
                    
                max_finish = max(task['PlannedFinish'] for task in valid_tasks)
                min_start = min(task['PlannedStart'] for task in valid_tasks)
                return (max_finish - min_start).days
            except Exception as e:
                st.warning(f"Could not calculate project duration: {str(e)}")
                return 0

        with col1:
            st.markdown("""
                <div class="metric-container">
                    <div class="metric-label">Total Tasks</div>
                    <div class="metric-value">{}</div>
                </div>
            """.format(len(task_details) if task_details else 0), unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div class="metric-container">
                    <div class="metric-label">Total Resources</div>
                    <div class="metric-value">{}</div>
                </div>
            """.format(len(resource_data) if project_resource_data else 0), unsafe_allow_html=True)

        with col3:
            total_cost = sum(cost['BudgetedCost'] for cost in task_costs) if task_costs else 0
            st.markdown("""
                <div class="metric-container">
                    <div class="metric-label">Total Budget</div>
                    <div class="metric-value">₹{:,.2f}</div>
                </div>
            """.format(total_cost), unsafe_allow_html=True)

        with col4:
            project_duration = calculate_project_duration(task_details)
            st.markdown("""
                <div class="metric-container">
                    <div class="metric-label">Project Duration</div>
                    <div class="metric-value">{} days</div>
                </div>
            """.format(project_duration), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Create tabs for different chart categories
        tab1, tab2, tab3 = st.tabs(["📊 Schedule Analysis", "💰 Cost Analysis", "🔄 Resource Analysis"])
        
        with tab1:
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            st.subheader("Task Schedule Overview")
            # Data for Planned Information
            #1. Task Vs Time
            wbs_task_data = []
            for wbs in wbs_details:
                for task in task_details:
                    if task['WBS'] == wbs['Id']:
                        wbs_task_data.append({
                            'WBSId': wbs['Id'], 
                            'WBSName': wbs['Name'],
                            'TaskId': task['Id'],
                            'PlannedStart': task['PlannedStart'],
                            'PlannedFinish': task['PlannedFinish']
                        })
            wbs_task_df = pd.DataFrame(wbs_task_data)
            st.subheader("1. Task Vs Time")
            with st.expander("Show Task Vs Time Data"):
                st.write(wbs_task_df)
            
            # Gantt Chart
            if not wbs_task_df.empty:
                fig = px.timeline(wbs_task_df, x_start="PlannedStart", x_end="PlannedFinish", y="TaskId", color="WBSName")
                fig.update_layout(
                    plot_bgcolor='rgba(54, 54, 54, 1)',
                    paper_bgcolor='rgba(54, 54, 54, 1)',
                    font_color='white',
                    xaxis_title_font_color='white',
                    yaxis_title_font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for Task Vs Time.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            # Cost analysis charts
            
        
            # 3. Cost vs Time
            cost_time_data = []
            for task in task_details:
                for resource_cost in resource_costs:
                    if task['Id'] == resource_cost['TaskId']:
                        planned_start = pd.to_datetime(task['PlannedStart']) if task['PlannedStart'] else None
                        planned_finish = pd.to_datetime(task['PlannedFinish']) if task['PlannedFinish'] else None
                        planned_duration = (planned_finish - planned_start).days if planned_start and planned_finish else None
                        cost_time_data.append({
                            'PlannedStart': planned_start,
                            'PlannedFinish': planned_finish,
                            'PlannedDuration': planned_duration,
                            'LaborCost': resource_cost['LaborCost'],
                            'MaterialCost': resource_cost['MaterialCost'],
                            'EquipmentCost': resource_cost['EquipmentCost'],
                            'OtherCost': resource_cost['OtherCost'],
                            'BudgetedCost': resource_cost['LaborCost'] + resource_cost['MaterialCost'] + resource_cost['EquipmentCost'] + resource_cost['OtherCost']
                        })
            cost_time_df = pd.DataFrame(cost_time_data)
            st.subheader("3. Cost Vs Time")
            with st.expander("Show Cost Vs Time Data"):
                st.write(cost_time_df)
            
            if not cost_time_df.empty and 'PlannedStart' in cost_time_df.columns and 'PlannedFinish' in cost_time_df.columns:
                min_date = cost_time_df['PlannedStart'].min()
                max_date = cost_time_df['PlannedFinish'].max()
                cost_time_df['Day'] = (cost_time_df['PlannedStart'] - min_date).dt.days
                
                fig = px.line(cost_time_df, x='Day', y=['LaborCost', 'MaterialCost', 'EquipmentCost', 'OtherCost', 'BudgetedCost'], title="Cost vs Time", labels={'value': 'Cost', 'variable': 'Cost Type'})
                fig.update_layout(
                    plot_bgcolor='rgba(54, 54, 54, 1)',
                    paper_bgcolor='rgba(54, 54, 54, 1)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                cost_time_df = cost_time_df.sort_values(by='Day')
                cost_time_df['Labor'] = cost_time_df['LaborCost'].cumsum()
                cost_time_df['Material'] = cost_time_df['MaterialCost'].cumsum()
                cost_time_df['Equipment'] = cost_time_df['EquipmentCost'].cumsum()
                cost_time_df['Other'] = cost_time_df['OtherCost'].cumsum()
                cost_time_df['Total'] = cost_time_df['BudgetedCost'].cumsum()
                
                st.subheader("Cumulative Cost vs Time and Resource Type Vs Cost")
                col1, col2 = st.columns(2)
                with col1:
                    fig_cumulative = px.line(cost_time_df, x='Day', y=['Labor', 'Material', 'Equipment', 'Other', 'Total'], title="Cumulative Cost vs Time", labels={'value': 'Cumulative Cost', 'variable': 'Cost Type'})
                    fig_cumulative.update_layout(
                        plot_bgcolor='rgba(54, 54, 54, 1)',
                        paper_bgcolor='rgba(54, 54, 54, 1)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_cumulative, use_container_width=True)
                
                with col2:
                    resource_type_df = pd.DataFrame(list(resource_type_costs.items()), columns=['ResourceType', 'TotalCost'])
                    fig = px.bar(resource_type_df, x='ResourceType', y='TotalCost', title="Resource Type Cost Share", labels={'TotalCost': 'Total Cost', 'ResourceType': 'Resource Type'}, color='ResourceType', color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                    fig.update_layout(
                        plot_bgcolor='rgba(54, 54, 54, 1)',
                        paper_bgcolor='rgba(54, 54, 54, 1)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("Show Resource Type Vs Cost Data"):
                        st.write(resource_type_df)
            else:
                st.warning("No data available for Cost Vs Time.")
            
            # Add Task vs Cost vs Time section before closing the container
            st.subheader("4. Task Vs Cost Vs Time")
            task_cost_data = []
            for task in task_details:
                for cost in task_costs:
                    if task['Id'] == cost['TaskId']:
                        planned_start = pd.to_datetime(task['PlannedStart']) if task['PlannedStart'] else None
                        planned_finish = pd.to_datetime(task['PlannedFinish']) if task['PlannedFinish'] else None
                        planned_duration = (planned_finish - planned_start).days if planned_start and planned_finish else None
                        task_cost_data.append({
                            'TaskId': task['Id'],
                            'PlannedStart': planned_start,
                            'PlannedFinish': planned_finish,
                            'PlannedDuration': planned_duration,
                            'BudgetedCost': cost['BudgetedCost']
                        })
            task_cost_df = pd.DataFrame(task_cost_data)
            
            with st.expander("Show Task Vs Cost Vs Time Data"):
                st.write(task_cost_df)
            
            if not task_cost_df.empty:
                fig = px.scatter(task_cost_df, x='PlannedStart', y='BudgetedCost', 
                               size='PlannedDuration', color='TaskId', 
                               title="Task Cost vs Time", 
                               labels={'BudgetedCost': 'Budgeted Cost', 'PlannedStart': 'Planned Start'})
                fig.update_layout(
                    plot_bgcolor='rgba(54, 54, 54, 1)',
                    paper_bgcolor='rgba(54, 54, 54, 1)',
                    font_color='white',
                    xaxis_title_font_color='white',
                    yaxis_title_font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for Task Vs Cost Vs Time.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            # Resource analysis charts
            #2. Resource Vs Task and Resource Units vs Time
            wbs_resource_data = []
            for wbs in wbs_details:
                for task in task_details:
                    for resource in resource_data:
                        if isinstance(resource, dict) and task['WBS'] == wbs['Id'] and task['Id'] == resource['Task']:
                            planned_start = task['PlannedStart']
                            planned_finish = task['PlannedFinish']
                            if planned_start and planned_finish:
                                days = (planned_finish - planned_start).days
                                units_per_day = resource['BudgetedUnits'] / days if days != 0 else 0
                                wbs_resource_data.append({
                                    'WBSId': wbs['Id'], 
                                    'WBSName': wbs['Name'],
                                    'TaskId': task['Id'],
                                    'ResourceId': resource['Resource'],
                                    'ResourceCategory': resource['ResourceCategory'],
                                    'BudgetedUnits': resource['BudgetedUnits'],
                                    'PlannedStart': planned_start,
                                    'PlannedFinish': planned_finish,
                                    'days': days,
                                    'units_per_day': units_per_day,
                                })
            wbs_resource_df = pd.DataFrame(wbs_resource_data)
            st.subheader("2. Resource Vs Task and Resource Units vs Time")
            with st.expander("Show Resource Vs Task and Resource Units vs Time Data"):
                st.write(wbs_resource_df)
            
            if not wbs_resource_df.empty and 'ResourceCategory' in wbs_resource_df.columns:
                resource_category_list = wbs_resource_df['ResourceCategory'].value_counts().index.tolist()
                selected_resource_category = st.selectbox("Select Resource Category", resource_category_list, key="resource_vs_task")
                
                if selected_resource_category:
                    filtered_df = wbs_resource_df[wbs_resource_df['ResourceCategory'] == selected_resource_category]
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.histogram(filtered_df, y='BudgetedUnits', x='WBSId', color='WBSId', title=f"Histogram of Budgeted Units for {selected_resource_category}")
                        fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                        fig.update_layout(
                            plot_bgcolor='rgba(54, 54, 54, 1)',
                            paper_bgcolor='rgba(54, 54, 54, 1)',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        fig_timeline = px.timeline(filtered_df, x_start="PlannedStart", x_end="PlannedFinish", y="TaskId", color="units_per_day", title=f"Timeline of Resource Units per Day for {selected_resource_category}")
                        fig_timeline.update_layout(
                            plot_bgcolor='rgba(54, 54, 54, 1)',
                            paper_bgcolor='rgba(54, 54, 54, 1)',
                            font_color='white'
                        )
                        st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    fig_hist = px.histogram(filtered_df, x='PlannedStart', y='units_per_day', title=f"Histogram of Units per Day for {selected_resource_category}")
                    fig_hist.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                    fig_hist.update_layout(
                        plot_bgcolor='rgba(54, 54, 54, 1)',
                        paper_bgcolor='rgba(54, 54, 54, 1)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("No data available for Resource Vs Task and Resource Units vs Time.")
                
            st.subheader("Cost Vs Task and Resource Category Vs Cost")
            col1, col2 = st.columns(2)
            with col1:
                wbs_resource_cost_data = []
                for wbs in wbs_details:
                    for task in task_details:
                        for resource_cost in resource_costs:
                            if task['WBS'] == wbs['Id'] and task['Id'] == resource_cost['TaskId']:
                                wbs_resource_cost_data.append({
                                    'WBSId': wbs['Id'], 
                                    'WBSName': wbs['Name'],
                                    'TaskId': task['Id'],
                                    'LaborCost': resource_cost['LaborCost'],
                                    'MaterialCost': resource_cost['MaterialCost'],
                                    'EquipmentCost': resource_cost['EquipmentCost'],
                                    'OtherCost': resource_cost['OtherCost'],
                                    'BudgetedCost': resource_cost['LaborCost'] + resource_cost['MaterialCost'] + resource_cost['EquipmentCost'] + resource_cost['OtherCost']
                                })
                wbs_resource_cost_df = pd.DataFrame(wbs_resource_cost_data)
                st.subheader("5. Cost Vs Task")
                with st.expander("Show Cost Vs Task Data"):
                    st.write(wbs_resource_cost_df)
                
                if not wbs_resource_cost_df.empty and 'WBSId' in wbs_resource_cost_df.columns:
                    fig = px.bar(
                        wbs_resource_cost_df, 
                        x='WBSId', 
                        y=['LaborCost', 'MaterialCost', 'EquipmentCost', 'OtherCost'], 
                        title="Cost Breakdown by WBS",
                        labels={'value': 'Cost', 'variable': 'Cost Type'},
                        barmode='stack'
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(54, 54, 54, 1)',
                        paper_bgcolor='rgba(54, 54, 54, 1)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for Cost Vs Task.")
            
            with col2:
                # Debugging information
                
                if resource_category_costs:
                    resource_category_df = pd.DataFrame(list(resource_category_costs.items()), columns=['ResourceCategory', 'TotalCost'])
                    st.subheader("6. Resource Category Vs Cost")
                    with st.expander("Show Resource Category Vs Cost Data"):
                        st.write(resource_category_df)
                    
                    fig = px.pie(resource_category_df, names='ResourceCategory', values='TotalCost', title="Resource Category Cost Share")
                    fig.update_traces(texttemplate='%{value:.2f}')
                    fig.update_layout(
                        plot_bgcolor='rgba(54, 54, 54, 1)',
                        paper_bgcolor='rgba(54, 54, 54, 1)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for Resource Category Vs Cost.")
            st.markdown('</div>', unsafe_allow_html=True)

# ...rest of existing code...
