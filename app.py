"""
Construction Material Recommendation System
A Streamlit application that recommends construction materials based on project 
specifications, environmental conditions, and cost factors.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from material_data import (
    generate_material_database, generate_supplier_database,
    MATERIAL_TYPES, APPLICATIONS
)
from data_utils import calculate_material_scores, filter_materials_by_application
from model import MaterialRecommender
from visualization import (
    visualize_material_comparison, visualize_cost_analysis,
    visualize_durability_vs_cost, visualize_environmental_impact,
    visualize_weather_resistance, visualize_material_scores,
    visualize_supplier_comparison
)

# Set page configuration
st.set_page_config(
    page_title="Construction Material Recommendation System",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if 'materials_df' not in st.session_state:
    st.session_state.materials_df = generate_material_database()

if 'suppliers_df' not in st.session_state:
    st.session_state.suppliers_df = generate_supplier_database()

if 'recommender' not in st.session_state:
    st.session_state.recommender = MaterialRecommender()

if 'project_specs' not in st.session_state:
    st.session_state.project_specs = {
        'applications': [],
        'material_types': [],
        'min_strength_mpa': 0,
        'min_durability_years': 0,
        'fire_resistance_requirement': 0,
        'water_resistance_requirement': 0,
        'thermal_requirement': None,
        'eco_friendly_requirement': 0,
        'budget_constraint': None,
        'installation_time_constraint': None,
        'environmental_conditions': {
            'heat': 0,
            'cold': 0,
            'humidity': 0,
            'uv': 0
        }
    }

if 'recommended_materials' not in st.session_state:
    st.session_state.recommended_materials = None

if 'selected_materials' not in st.session_state:
    st.session_state.selected_materials = []

if 'project_area' not in st.session_state:
    st.session_state.project_area = 100.0

def update_project_specs():
    """Update project specifications based on user input."""
    # Update the project specifications
    st.session_state.project_specs = {
        'applications': st.session_state.applications,
        'material_types': st.session_state.material_types,
        'min_strength_mpa': st.session_state.min_strength,
        'min_durability_years': st.session_state.min_durability,
        'fire_resistance_requirement': st.session_state.fire_resistance,
        'water_resistance_requirement': st.session_state.water_resistance,
        'thermal_requirement': st.session_state.thermal_requirement,
        'eco_friendly_requirement': st.session_state.eco_friendly,
        'budget_constraint': st.session_state.budget,
        'installation_time_constraint': st.session_state.installation_time,
        'environmental_conditions': {
            'heat': st.session_state.heat_importance,
            'cold': st.session_state.cold_importance,
            'humidity': st.session_state.humidity_importance,
            'uv': st.session_state.uv_importance
        }
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

def main():
    """Main function to render the Streamlit application."""
    st.title("🏗️ Construction Material Recommendation System")
    st.subheader("AI-powered material selection for construction projects")
    
    # Create tabs for different sections
    tabs = st.tabs([
        "Project Specifications", 
        "Material Recommendations", 
        "Material Comparison", 
        "Cost Analysis",
        "Help"
    ])
    
    # Tab 1: Project Specifications
    with tabs[0]:
        st.header("Project Specifications")
        st.info("Define your project requirements to get material recommendations.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Project Information")
            
            # Application selection
            st.selectbox(
                "Application",
                options=APPLICATIONS,
                key="applications"
            )
            
            # Material type preferences
            st.multiselect(
                "Preferred Material Types (optional)",
                options=MATERIAL_TYPES,
                default=[],
                key="material_types"
            )
            
            # Strength requirements
            st.slider(
                "Minimum Strength (MPa)",
                min_value=0,
                max_value=500,
                value=0,
                step=5,
                key="min_strength"
            )
            
            # Durability requirements
            st.slider(
                "Minimum Durability (years)",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                key="min_durability"
            )
            
            # Budget constraint
            st.number_input(
                "Budget Constraint ($ per unit)",
                min_value=0.0,
                max_value=10000.0,
                value=0.0,
                step=10.0,
                key="budget"
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
                key="fire_resistance"
            )
            
            # Water resistance
            st.slider(
                "Water Resistance Requirement (1-10)",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key="water_resistance"
            )
            
            # Thermal requirements
            st.selectbox(
                "Thermal Conductivity Requirement",
                options=[None, 'low', 'high'],
                format_func=lambda x: 'None' if x is None else ('Low (good insulation)' if x == 'low' else 'High (good conductor)'),
                key="thermal_requirement"
            )
            
            # Eco-friendly requirements
            st.slider(
                "Eco-Friendly Requirement (1-10)",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key="eco_friendly"
            )
            
            # Installation time constraint
            st.selectbox(
                "Installation Time Constraint",
                options=[None, 'low', 'high'],
                format_func=lambda x: 'None' if x is None else ('Low (quick installation needed)' if x == 'low' else 'High (complex installation acceptable)'),
                key="installation_time"
            )
        
        st.subheader("Environmental Conditions")
        st.info("Rate the importance of resistance to each environmental condition (0 = not important, 10 = very important)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.slider(
                "Heat Resistance",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key="heat_importance"
            )
        
        with col2:
            st.slider(
                "Cold Resistance",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key="cold_importance"
            )
        
        with col3:
            st.slider(
                "Humidity Resistance",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key="humidity_importance"
            )
        
        with col4:
            st.slider(
                "UV Resistance",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key="uv_importance"
            )
        
        # Get recommendations button
        st.button(
            "Get Material Recommendations",
            on_click=get_recommendations,
            type="primary"
        )
    
    # Tab 2: Material Recommendations
    with tabs[1]:
        st.header("Material Recommendations")
        
        if st.session_state.recommended_materials is not None:
            # Display the recommendation scores visualization
            score_fig = visualize_material_scores(st.session_state.recommended_materials)
            if score_fig:
                st.plotly_chart(score_fig, use_container_width=True)
            
            # Display the recommended materials in a table
            st.subheader("Top Recommended Materials")
            
            # Create a table with the top 5 materials
            for i, (_, material) in enumerate(st.session_state.recommended_materials.head(5).iterrows()):
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
                    if material['id'] in st.session_state.selected_materials:
                        st.button(
                            "Remove from Comparison",
                            key=f"remove_{material['id']}",
                            on_click=remove_from_comparison,
                            args=(material['id'],)
                        )
                    else:
                        st.button(
                            "Add to Comparison",
                            key=f"add_{material['id']}",
                            on_click=add_to_comparison,
                            args=(material['id'],)
                        )
                
                st.divider()
            
            # Display durability vs cost chart for all materials
            st.subheader("Durability vs. Cost Analysis")
            durability_cost_fig = visualize_durability_vs_cost(st.session_state.materials_df)
            st.plotly_chart(durability_cost_fig, use_container_width=True)
        else:
            st.info("Enter your project specifications and click 'Get Material Recommendations' to see recommendations.")
    
    # Tab 3: Material Comparison
    with tabs[2]:
        st.header("Material Comparison")
        
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
                    material = st.session_state.materials_df[st.session_state.materials_df['id'] == material_id].iloc[0]
                    st.write(f"**{material['name']}**")
                    st.button(
                        "Remove",
                        key=f"remove_comp_{material_id}",
                        on_click=remove_from_comparison,
                        args=(material_id,)
                    )
            
            # Add a button to clear all comparisons
            st.button(
                "Clear All Comparisons",
                on_click=clear_comparison
            )
            
            # Display radar chart comparison
            st.subheader("Property Comparison")
            radar_fig = visualize_material_comparison(
                st.session_state.materials_df, 
                st.session_state.selected_materials
            )
            if radar_fig:
                st.plotly_chart(radar_fig, use_container_width=True)
            
            # Display environmental impact comparison
            st.subheader("Environmental Impact Comparison")
            eco_fig = visualize_environmental_impact(
                st.session_state.materials_df, 
                st.session_state.selected_materials
            )
            if eco_fig:
                st.plotly_chart(eco_fig, use_container_width=True)
            
            # Display weather resistance comparison
            st.subheader("Weather Resistance Comparison")
            weather_fig = visualize_weather_resistance(
                st.session_state.materials_df, 
                st.session_state.selected_materials
            )
            if weather_fig:
                st.plotly_chart(weather_fig, use_container_width=True)
            
            # Display supplier information
            st.subheader("Supplier Information")
            
            # Get suppliers for selected materials
            supplier_ids = []
            for material_id in st.session_state.selected_materials:
                material = st.session_state.materials_df[st.session_state.materials_df['id'] == material_id].iloc[0]
                supplier_id = material['supplier_id']
                if supplier_id not in supplier_ids:
                    supplier_ids.append(supplier_id)
            
            # Display supplier comparison
            supplier_fig = visualize_supplier_comparison(
                st.session_state.suppliers_df,
                supplier_ids
            )
            if supplier_fig:
                st.plotly_chart(supplier_fig, use_container_width=True)
            
            # Display supplier details
            for supplier_id in supplier_ids:
                supplier = st.session_state.suppliers_df[st.session_state.suppliers_df['supplier_id'] == supplier_id].iloc[0]
                st.write(f"**{supplier['name']}** ({supplier['supplier_id']})")
                st.write(f"Location: {supplier['location']}")
                st.write(f"Price Level: {supplier['price_level']}")
                st.write(f"Delivery Time: {supplier['delivery_time_days']} days")
                st.write(f"Reliability Score: {supplier['reliability_score']}/10")
                st.write(f"Contact: {supplier['contact']}")
                st.divider()
    
    # Tab 4: Cost Analysis
    with tabs[3]:
        st.header("Cost Analysis")
        
        if not st.session_state.selected_materials:
            st.info("Add materials to comparison from the Recommendations tab to perform cost analysis.")
        else:
            st.subheader("Project Cost Estimation")
            
            # Input project size
            col1, col2 = st.columns(2)
            with col1:
                project_area = st.number_input(
                    "Project Size (units, e.g., square meters, cubic meters, etc.)",
                    min_value=1.0,
                    max_value=10000.0,
                    value=st.session_state.project_area,
                    step=10.0,
                    key="project_area_input"
                )
                st.session_state.project_area = project_area
            
            # Display cost analysis chart
            cost_fig = visualize_cost_analysis(
                st.session_state.materials_df,
                st.session_state.selected_materials,
                st.session_state.project_area
            )
            if cost_fig:
                st.plotly_chart(cost_fig, use_container_width=True)
            
            # Display cost breakdown table
            st.subheader("Cost Breakdown")
            
            # Create a table with cost details
            cost_data = []
            for material_id in st.session_state.selected_materials:
                material = st.session_state.materials_df[st.session_state.materials_df['id'] == material_id].iloc[0]
                cost_data.append({
                    'Material': material['name'],
                    'Cost per Unit': f"${material['cost_per_unit']:.2f}",
                    'Project Size': f"{st.session_state.project_area} units",
                    'Total Cost': f"${material['cost_per_unit'] * st.session_state.project_area:.2f}"
                })
            
            cost_df = pd.DataFrame(cost_data)
            st.table(cost_df)
            
            # Additional cost considerations
            st.subheader("Additional Cost Considerations")
            st.write("""
            - **Installation Costs**: More complex materials typically have higher installation costs.
            - **Maintenance Costs**: Consider long-term maintenance requirements over the material's lifetime.
            - **Replacement Frequency**: Higher durability materials may have higher upfront costs but lower replacement frequency.
            - **Energy Efficiency**: Some materials may provide energy savings over time.
            """)
    
    # Tab 5: Help
    with tabs[4]:
        st.header("Help & Information")
        
        st.subheader("About the System")
        st.write("""
        This AI-powered Construction Material Recommendation System helps you select 
        the most suitable materials for your construction project based on your specific 
        requirements, environmental conditions, and budget constraints.
        """)
        
        st.subheader("How to Use")
        st.write("""
        1. **Enter Project Specifications**: In the first tab, provide details about your project requirements.
        2. **Get Recommendations**: Click the "Get Material Recommendations" button to receive AI-generated recommendations.
        3. **Compare Materials**: Add materials to the comparison tool to evaluate their properties side by side.
        4. **Analyze Costs**: Estimate project costs based on material prices and project size.
        """)
        
        st.subheader("Understanding Material Properties")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Physical Properties:**")
            st.write("- **Strength**: Resistance to deformation under load (MPa)")
            st.write("- **Durability**: Expected service life in years")
            st.write("- **Thermal Conductivity**: Heat transfer capability (W/m·K)")
            st.write("- **Fire Resistance**: Time material can withstand fire (hours)")
            st.write("- **Water Resistance**: Ability to repel water (1-10 scale)")
        
        with col2:
            st.write("**Other Factors:**")
            st.write("- **Eco-Friendly Score**: Environmental impact rating (1-10)")
            st.write("- **Installation Complexity**: Difficulty of installation (1-10)")
            st.write("- **Maintenance Requirement**: Level of upkeep needed (1-10)")
            st.write("- **Weather Resistance**: Performance in different weather conditions")
            st.write("- **Availability**: Ease of sourcing the material (1-10)")

if __name__ == "__main__":
    main()
