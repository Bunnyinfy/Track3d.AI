"""
Construction Material Recommendation System
A Streamlit application that recommends construction materials based on project
specifications, environmental conditions, and cost factors.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_option_menu import option_menu
import os
import json

# Import local modules
from material_data import (
    generate_material_database,
    generate_supplier_database,
    MATERIAL_TYPES,
    APPLICATIONS,
)
from data_utils import calculate_material_scores, filter_materials_by_application
from model import MaterialRecommender
from visualization import (
    visualize_material_comparison,
    visualize_cost_analysis,
    visualize_durability_vs_cost,
    visualize_environmental_impact,
    visualize_weather_resistance,
    visualize_material_scores,
    visualize_supplier_comparison,
)
from auth import display_login_page, logout_user
from projects import display_user_projects, display_save_project_form
from init_db import init_database

# Set page configuration
st.set_page_config(
    page_title="BuildWise - Construction Material Recommendation System",
    page_icon="🧱",
    layout="wide",
)

# Custom CSS for better appearance
st.markdown(
    """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #34495e;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5;
        color: white;
    }
    div[data-testid="stSidebarContent"] > div:nth-child(1) {
        padding-top: 2rem;
    }
    .css-1544g2n {
        padding-top: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize database if needed
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# Initialize session state
if "materials_df" not in st.session_state:
    st.session_state.materials_df = generate_material_database()

if "suppliers_df" not in st.session_state:
    st.session_state.suppliers_df = generate_supplier_database()

if "recommender" not in st.session_state:
    st.session_state.recommender = MaterialRecommender()

if "project_specs" not in st.session_state:
    st.session_state.project_specs = {
        "applications": [],
        "material_types": [],
        "min_strength_mpa": 0,
        "min_durability_years": 0,
        "fire_resistance_requirement": 0,
        "water_resistance_requirement": 0,
        "thermal_requirement": None,
        "eco_friendly_requirement": 0,
        "budget_constraint": None,
        "installation_time_constraint": None,
        "environmental_conditions": {"heat": 0, "cold": 0, "humidity": 0, "uv": 0},
    }

if "recommended_materials" not in st.session_state:
    st.session_state.recommended_materials = None

if "selected_materials" not in st.session_state:
    st.session_state.selected_materials = []

if "project_area" not in st.session_state:
    st.session_state.project_area = 100.0


def update_project_specs():
    """Update project specifications based on user input."""
    # Update the project specifications
    st.session_state.project_specs = {
        "applications": st.session_state.applications,
        "material_types": st.session_state.material_types,
        "min_strength_mpa": st.session_state.min_strength,
        "min_durability_years": st.session_state.min_durability,
        "fire_resistance_requirement": st.session_state.fire_resistance,
        "water_resistance_requirement": st.session_state.water_resistance,
        "thermal_requirement": st.session_state.thermal_requirement,
        "eco_friendly_requirement": st.session_state.eco_friendly,
        "budget_constraint": st.session_state.budget,
        "installation_time_constraint": st.session_state.installation_time,
        "environmental_conditions": {
            "heat": st.session_state.heat_importance,
            "cold": st.session_state.cold_importance,
            "humidity": st.session_state.humidity_importance,
            "uv": st.session_state.uv_importance,
        },
    }


def get_recommendations():
    """Get material recommendations based on project specifications."""
    # Update project specs
    update_project_specs()

    # Get recommendations
    recommended_materials = st.session_state.recommender.recommend_materials(
        st.session_state.project_specs, n_recommendations=10
    )

    # Update session state
    st.session_state.recommended_materials = recommended_materials


def add_to_comparison(material_id):
    """Add a material to the comparison list."""
    if material_id not in st.session_state.selected_materials:
        st.session_state.selected_materials.append(material_id)


def remove_from_comparison(material_id):
    """Remove a material from the comparison list."""
    if material_id in st.session_state.selected_materials:
        st.session_state.selected_materials.remove(material_id)


def clear_comparison():
    """Clear the comparison list."""
    st.session_state.selected_materials = []


def display_project_specifications():
    """Display the project specifications form."""
    st.header("Project Specifications")
    st.info("Define your project requirements to get material recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Basic Project Information")

        # Application selection
        st.selectbox("Application", options=APPLICATIONS, key="applications")

        # Material type preferences
        st.multiselect(
            "Preferred Material Types (optional)",
            options=MATERIAL_TYPES,
            default=[],
            key="material_types",
        )

        # Strength requirements
        st.slider(
            "Minimum Strength (MPa)",
            min_value=0,
            max_value=500,
            value=0,
            step=5,
            key="min_strength",
        )

        # Durability requirements
        st.slider(
            "Minimum Durability (years)",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            key="min_durability",
        )

        # Budget constraint
        st.number_input(
            "Budget Constraint ($ per unit)",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=10.0,
            key="budget",
        )

    with col2:
        st.subheader("Performance Requirements")

        # Fire resistance
        st.slider(
            "Fire Resistance Requirement (hours)",
            min_value=0.0,
            max_value=6.0,
            value=0.0,
            step=0.5,
            key="fire_resistance",
        )

        # Water resistance
        st.slider(
            "Water Resistance Requirement (1-10)",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="water_resistance",
        )

        # Thermal requirements
        st.selectbox(
            "Thermal Conductivity Requirement",
            options=[None, "low", "high"],
            format_func=lambda x: (
                "None"
                if x is None
                else (
                    "Low (good insulation)" if x == "low" else "High (good conductor)"
                )
            ),
            key="thermal_requirement",
        )

        # Eco-friendly requirements
        st.slider(
            "Eco-Friendly Requirement (1-10)",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="eco_friendly",
        )

        # Installation time constraint
        st.selectbox(
            "Installation Time Constraint",
            options=[None, "low", "high"],
            format_func=lambda x: (
                "None"
                if x is None
                else (
                    "Low (quick installation needed)"
                    if x == "low"
                    else "High (complex installation acceptable)"
                )
            ),
            key="installation_time",
        )

    st.subheader("Environmental Conditions")
    st.info(
        "Rate the importance of resistance to each environmental condition (0 = not important, 10 = very important)"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.slider(
            "Heat Resistance",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="heat_importance",
        )

    with col2:
        st.slider(
            "Cold Resistance",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="cold_importance",
        )

    with col3:
        st.slider(
            "Humidity Resistance",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="humidity_importance",
        )

    with col4:
        st.slider(
            "UV Resistance",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="uv_importance",
        )

    # Get recommendations button
    if st.button(
        "Get Material Recommendations",
        on_click=get_recommendations,
        type="primary",
        use_container_width=True,
    ):
        pass


def display_recommendations():
    """Display the recommendations."""
    st.header("Material Recommendations")
    st.info("Top materials for your project based on your specifications")

    if st.session_state.recommended_materials is not None:
        # Display the recommendation scores visualization
        score_fig = visualize_material_scores(st.session_state.recommended_materials)
        if score_fig:
            st.plotly_chart(score_fig, use_container_width=True)

        # Display the recommended materials in a table
        st.subheader("Top Recommended Materials")

        # Create a table with the top 5 materials
        for i, (_, material) in enumerate(
            st.session_state.recommended_materials.head(5).iterrows()
        ):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**{i+1}. {material['name']}** ({material['type']})")
                st.write(f"Applications: {', '.join(material['applications'])}")
                st.write(f"Score: {material['total_score']:.2f}/10")

            with col2:
                st.write(f"Strength: {material['strength_mpa']} MPa")
                st.write(f"Durability: {material['durability_years']} years")
                st.write(f"Cost: ${material['cost_per_unit']:.2f} per unit")

            with col3:
                if material["id"] in st.session_state.selected_materials:
                    st.button(
                        "⛔ Remove",
                        key=f"remove_{material['id']}",
                        on_click=remove_from_comparison,
                        args=(material["id"],),
                    )
                else:
                    st.button(
                        "➕ Compare",
                        key=f"add_{material['id']}",
                        on_click=add_to_comparison,
                        args=(material["id"],),
                    )

            st.divider()

        # Display durability vs cost chart for all materials
        st.subheader("Durability vs. Cost Analysis")
        durability_cost_fig = visualize_durability_vs_cost(
            st.session_state.materials_df
        )
        st.plotly_chart(durability_cost_fig, use_container_width=True)
    else:
        st.info(
            "Enter your project specifications and click 'Get Material Recommendations' to see recommendations."
        )


def display_comparison():
    """Display the material comparison."""
    st.header("Material Comparison")
    st.info("Compare different materials side by side")

    if not st.session_state.selected_materials:
        st.info("Add materials to comparison from the Recommendations tab.")
    else:
        # Show selected materials
        st.subheader("Selected Materials for Comparison")

        # Create a list of selected materials with remove buttons
        cols = st.columns(min(len(st.session_state.selected_materials), 4))
        for i, material_id in enumerate(st.session_state.selected_materials):
            col_index = i % len(cols)
            with cols[col_index]:
                material = st.session_state.materials_df[
                    st.session_state.materials_df["id"] == material_id
                ].iloc[0]
                st.write(f"**{material['name']}**")
                st.button(
                    "Remove",
                    key=f"remove_comp_{material_id}",
                    on_click=remove_from_comparison,
                    args=(material_id,),
                )

        # Add a button to clear all comparisons
        st.button("Clear All Comparisons", on_click=clear_comparison, type="secondary")

        # Display radar chart comparison
        st.subheader("Property Comparison")
        radar_fig = visualize_material_comparison(
            st.session_state.materials_df, st.session_state.selected_materials
        )
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)

        # Display environmental impact comparison
        st.subheader("Environmental Impact Comparison")
        eco_fig = visualize_environmental_impact(
            st.session_state.materials_df, st.session_state.selected_materials
        )
        if eco_fig:
            st.plotly_chart(eco_fig, use_container_width=True)

        # Display weather resistance comparison
        st.subheader("Weather Resistance Comparison")
        weather_fig = visualize_weather_resistance(
            st.session_state.materials_df, st.session_state.selected_materials
        )
        if weather_fig:
            st.plotly_chart(weather_fig, use_container_width=True)

        # Display supplier information
        st.subheader("Supplier Information")

        # Get suppliers for selected materials
        supplier_ids = []
        for material_id in st.session_state.selected_materials:
            material = st.session_state.materials_df[
                st.session_state.materials_df["id"] == material_id
            ].iloc[0]
            supplier_id = material["supplier_id"]
            if supplier_id not in supplier_ids:
                supplier_ids.append(supplier_id)

        # Display supplier comparison
        supplier_fig = visualize_supplier_comparison(
            st.session_state.suppliers_df, supplier_ids
        )
        if supplier_fig:
            st.plotly_chart(supplier_fig, use_container_width=True)

        # Display supplier details
        for supplier_id in supplier_ids:
            supplier = st.session_state.suppliers_df[
                st.session_state.suppliers_df["supplier_id"] == supplier_id
            ].iloc[0]
            st.write(f"**{supplier['name']}** ({supplier['supplier_id']})")
            st.write(f"Location: {supplier['location']}")
            st.write(f"Price Level: {supplier['price_level']}")
            st.write(f"Delivery Time: {supplier['delivery_time_days']} days")
            st.write(f"Reliability Score: {supplier['reliability_score']}/10")
            st.write(f"Contact: {supplier['contact']}")
            st.divider()


def display_cost_analysis():
    """Display the cost analysis."""
    st.header("Cost Analysis")
    st.info("Analyze the cost implications of different materials")

    if not st.session_state.selected_materials:
        st.info("Add materials to comparison from the Recommendations tab.")
    else:
        # Project area input
        st.number_input(
            "Project Size (area or quantity)",
            min_value=1.0,
            max_value=10000.0,
            value=st.session_state.project_area,
            step=10.0,
            key="project_area",
            on_change=lambda: setattr(
                st.session_state, "project_area", st.session_state.project_area
            ),
        )

        # Display cost analysis
        st.subheader("Material Cost Comparison")
        cost_fig = visualize_cost_analysis(
            st.session_state.materials_df,
            st.session_state.selected_materials,
            st.session_state.project_area,
        )
        if cost_fig:
            st.plotly_chart(cost_fig, use_container_width=True)

        # Display cost table
        st.subheader("Detailed Cost Breakdown")

        cost_data = []
        for material_id in st.session_state.selected_materials:
            material = st.session_state.materials_df[
                st.session_state.materials_df["id"] == material_id
            ].iloc[0]
            total_cost = material["cost_per_unit"] * st.session_state.project_area

            cost_data.append(
                {
                    "Material": material["name"],
                    "Type": material["type"],
                    "Cost per Unit": f"${material['cost_per_unit']:.2f}",
                    "Project Size": st.session_state.project_area,
                    "Total Cost": f"${total_cost:.2f}",
                }
            )

        cost_df = pd.DataFrame(cost_data)
        st.dataframe(cost_df, use_container_width=True)


def display_user_dashboard():
    """Display the user dashboard."""
    st.header("User Dashboard")
    st.info("Manage your saved projects")

    # Display user projects
    display_user_projects(st.session_state.user_id)

    st.divider()

    # Display save project form
    display_save_project_form(st.session_state.user_id)


def display_help():
    """Display the help section."""
    st.header("Help & Information")
    st.info("Learn how to use the Construction Material Recommendation System")

    st.subheader("About the System")
    st.write(
        """
    The Construction Material Recommendation System helps you select the best materials for your construction project based on your specific requirements. 
    The system analyzes various material properties, environmental conditions, and cost factors to provide intelligent recommendations.
    """
    )

    st.subheader("How to Use")
    st.write(
        """
    1. **Project Specifications**: Define your project requirements, including application, strength, durability, budget, and environmental conditions.
    2. **Material Recommendations**: View recommended materials based on your specifications.
    3. **Material Comparison**: Add materials to comparison to evaluate their properties side by side.
    4. **Cost Analysis**: Analyze the cost implications of different materials for your project.
    5. **User Dashboard**: Save and manage your projects for future reference.
    """
    )

    st.subheader("Material Properties")
    st.write(
        """
    - **Strength**: Material's resistance to deformation, measured in Megapascals (MPa).
    - **Durability**: Expected lifespan of the material in years.
    - **Thermal Conductivity**: Rate of heat transfer through the material.
    - **Fire Resistance**: Time the material can withstand fire exposure.
    - **Water Resistance**: Material's ability to resist water penetration (scale 1-10).
    - **Eco-Friendly Score**: Environmental impact assessment (scale 1-10).
    """
    )

    st.subheader("Contact Information")
    st.write(
        """
    For more information or assistance, please contact us at:
    - Email: penugondasrinivas20@gmail.com
    - Phone: (+91) 7995787167
    """
    )


def main():
    """Main function to render the Streamlit application."""
    # First, check if user is logged in
    is_logged_in = display_login_page()

    if not is_logged_in:
        return

    # Show app header
    st.markdown(
        '<div class="main-header">🏗️ Construction Material Recommendation System</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">AI-powered material selection for construction projects</div>',
        unsafe_allow_html=True,
    )

    # Add a sidebar with user information and navigation
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.username}!")

        # Navigation menu
        if "selected_menu" not in st.session_state:
            st.session_state.selected_menu = 0

        menu_options = [
            "Project Specifications",
            "Recommendations",
            "Material Comparison",
            "Cost Analysis",
            "My Projects",
            "Help",
        ]

        if "selected_menu" not in st.session_state:
            st.session_state.selected_menu = 0

        # Update selected_menu before rendering option_menu to avoid double click issue
        if "selected_menu" not in st.session_state:
            st.session_state.selected_menu = 0

        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=[
                "pencil-square",
                "list-check",
                "bar-chart",
                "cash-coin",
                "folder",
                "question-circle",
            ],
            default_index=st.session_state.selected_menu,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "orange", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#4e8df5"},
            },
        )

        st.divider()

        # Logout button
        if st.button("Logout", type="secondary", use_container_width=True):
            logout_user()
            st.rerun()

    # Display the selected section
    if selected == "Project Specifications":
        display_project_specifications()
    elif selected == "Recommendations":
        display_recommendations()
    elif selected == "Material Comparison":
        display_comparison()
    elif selected == "Cost Analysis":
        display_cost_analysis()
    elif selected == "My Projects":
        display_user_dashboard()
    elif selected == "Help":
        display_help()

    # Update the selected menu in session state only if changed
    new_index = menu_options.index(selected)
    if st.session_state.selected_menu != new_index:
        st.session_state.selected_menu = new_index


if __name__ == "__main__":
    main()
