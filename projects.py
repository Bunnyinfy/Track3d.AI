"""
Projects module for the construction material recommendation system.
This module handles user projects and their management.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from db_utils import (
    save_user_project, get_user_projects, delete_user_project, 
    get_project_by_id, update_user_project
)


def save_current_project(user_id, project_name=None):
    """
    Save the current project.
    
    Args:
        user_id (int): User ID
        project_name (str, optional): Project name. Defaults to None.
        
    Returns:
        tuple: (success, message)
    """
    if 'project_specs' not in st.session_state:
        return False, "No project to save."
    
    if not project_name:
        project_name = f"Project {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    project_id = save_user_project(user_id, project_name, st.session_state.project_specs)
    
    if project_id:
        return True, f"Project '{project_name}' saved successfully!"
    else:
        return False, "Failed to save project."


def load_project(project_id, user_id):
    """
    Load a project.
    
    Args:
        project_id (int): Project ID
        user_id (int): User ID
        
    Returns:
        tuple: (success, message)
    """
    project = get_project_by_id(project_id, user_id)
    
    if project:
        st.session_state.project_specs = project['specs']
        
        # Update all the individual state variables
        specs = project['specs']
        
        # Applications
        if 'applications' in specs:
            st.session_state.applications = specs['applications']
        
        # Material types
        if 'material_types' in specs:
            st.session_state.material_types = specs['material_types']
        
        # Numerical values
        if 'min_strength_mpa' in specs:
            st.session_state.min_strength = specs['min_strength_mpa']
        
        if 'min_durability_years' in specs:
            st.session_state.min_durability = specs['min_durability_years']
        
        if 'fire_resistance_requirement' in specs:
            st.session_state.fire_resistance = specs['fire_resistance_requirement']
        
        if 'water_resistance_requirement' in specs:
            st.session_state.water_resistance = specs['water_resistance_requirement']
        
        if 'thermal_requirement' in specs:
            st.session_state.thermal_requirement = specs['thermal_requirement']
        
        if 'eco_friendly_requirement' in specs:
            st.session_state.eco_friendly = specs['eco_friendly_requirement']
        
        if 'budget_constraint' in specs:
            st.session_state.budget = specs['budget_constraint']
        
        if 'installation_time_constraint' in specs:
            st.session_state.installation_time = specs['installation_time_constraint']
        
        # Environmental conditions
        if 'environmental_conditions' in specs:
            env = specs['environmental_conditions']
            if 'heat' in env:
                st.session_state.heat_importance = env['heat']
            if 'cold' in env:
                st.session_state.cold_importance = env['cold']
            if 'humidity' in env:
                st.session_state.humidity_importance = env['humidity']
            if 'uv' in env:
                st.session_state.uv_importance = env['uv']
        
        return True, f"Project '{project['name']}' loaded successfully!"
    else:
        return False, "Failed to load project."


def update_project(project_id, user_id, project_name=None):
    """
    Update an existing project.
    
    Args:
        project_id (int): Project ID
        user_id (int): User ID
        project_name (str, optional): Project name. Defaults to None.
        
    Returns:
        tuple: (success, message)
    """
    if 'project_specs' not in st.session_state:
        return False, "No project to update."
    
    current_project = get_project_by_id(project_id, user_id)
    if not current_project:
        return False, "Project not found."
    
    if not project_name:
        project_name = current_project['name']
    
    success = update_user_project(project_id, user_id, project_name, st.session_state.project_specs)
    
    if success:
        return True, f"Project '{project_name}' updated successfully!"
    else:
        return False, "Failed to update project."


def display_user_projects(user_id):
    """
    Display user projects.
    
    Args:
        user_id (int): User ID
    """
    st.subheader("Your Projects")
    
    projects = get_user_projects(user_id)
    
    if not projects:
        st.info("You don't have any saved projects yet.")
        return
    
    # Display projects in a data frame with action buttons
    project_data = []
    for project in projects:
        project_data.append({
            "ID": project['id'],
            "Name": project['name'],
            "Created": project['created_at'].strftime("%Y-%m-%d %H:%M"),
            "Last Updated": project['updated_at'].strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(project_data)
    
    # Use st.dataframe with a column config to create action buttons
    st.dataframe(
        df,
        column_config={
            "ID": None,  # Hide ID column
        },
        hide_index=True
    )
    
    # Project actions
    cols = st.columns(3)
    
    with cols[0]:
        selected_project_id = st.selectbox(
            "Select a project",
            options=[p['id'] for p in projects],
            format_func=lambda x: next((p['name'] for p in projects if p['id'] == x), "")
        )
    
    with cols[1]:
        if st.button("Load Project", key="load_project_button"):
            if selected_project_id:
                success, message = load_project(selected_project_id, user_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with cols[2]:
        if st.button("Delete Project", key="delete_project_button"):
            if selected_project_id:
                if delete_user_project(selected_project_id, user_id):
                    st.success("Project deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete project.")


def display_save_project_form(user_id):
    """
    Display a form to save or update the current project.
    
    Args:
        user_id (int): User ID
    """
    st.subheader("Save Project")
    
    project_name = st.text_input("Project Name", key="save_project_name")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save as New Project", key="save_new_project_button"):
            if 'project_specs' in st.session_state:
                success, message = save_current_project(user_id, project_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please configure project specifications before saving.")
    
    with col2:
        # Get user's projects for the dropdown
        projects = get_user_projects(user_id)
        if projects:
            project_options = [(p['id'], p['name']) for p in projects]
            selected_project = st.selectbox(
                "Update Existing Project",
                options=project_options,
                format_func=lambda x: x[1]
            )
            
            if st.button("Update Project", key="update_project_button"):
                if 'project_specs' in st.session_state:
                    success, message = update_project(selected_project[0], user_id, project_name or selected_project[1])
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please configure project specifications before updating.")