"""
Construction Material Recommendation System
A Flask web application that recommends construction materials based on project 
specifications, environmental conditions, and cost factors.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import uuid
from material_data import (
    generate_material_database, generate_supplier_database,
    MATERIAL_TYPES, APPLICATIONS
)
from data_utils import calculate_material_scores, filter_materials_by_application
from model import MaterialRecommender
from database import init_db, seed_database, db, Material, Supplier, Project, Recommendation, UserFeedback
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize data
materials_df = generate_material_database()
suppliers_df = generate_supplier_database()
recommender = MaterialRecommender()

# Initialize and seed the database
init_db(app)
seed_database(app, materials_df, suppliers_df)

def create_material_comparison_chart(selected_material_ids):
    """
    Create a radar chart comparing material properties.
    
    Args:
        selected_material_ids (list): List of selected material IDs
        
    Returns:
        JSON: JSON string for plotly chart
    """
    if not selected_material_ids:
        return None
    
    # Filter materials by selected IDs
    selected_materials = materials_df[materials_df['id'].isin(selected_material_ids)]
    
    # Properties to compare
    properties = [
        'strength_mpa', 'durability_years', 'fire_resistance_hours', 
        'water_resistance', 'eco_friendly_score', 'cost_per_unit',
        'maintenance_requirement', 'installation_complexity'
    ]
    
    # Short display names for the properties
    property_names = [
        'Strength', 'Durability', 'Fire Resistance', 
        'Water Resistance', 'Eco-Friendly', 'Cost (inv)',
        'Maintenance (inv)', 'Installation (inv)'
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Normalize properties for radar chart
    normalized_data = {}
    for prop in properties:
        max_val = max(selected_materials[prop].max(), 1)  # Avoid division by zero
        
        # For cost and complexity, lower is better, so we invert
        if prop in ['cost_per_unit', 'maintenance_requirement', 'installation_complexity']:
            normalized_data[prop] = 1 - (selected_materials[prop] / max_val)
        else:
            normalized_data[prop] = selected_materials[prop] / max_val
    
    # Add traces for each material
    for _, material in selected_materials.iterrows():
        values = [normalized_data[prop].loc[material.name] for prop in properties]
        values.append(values[0])  # Close the loop
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=property_names + [property_names[0]],  # Close the loop
            fill='toself',
            name=material['name']
        ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="Material Properties Comparison"
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_environmental_impact_chart(selected_material_ids):
    """
    Create a bar chart of eco-friendly scores.
    
    Args:
        selected_material_ids (list): List of selected material IDs
        
    Returns:
        JSON: JSON string for plotly chart
    """
    if not selected_material_ids:
        return None
    
    # Filter materials by selected IDs
    selected_materials = materials_df[materials_df['id'].isin(selected_material_ids)]
    
    # Sort by eco-friendly score
    selected_materials = selected_materials.sort_values(by='eco_friendly_score', ascending=False)
    
    # Create figure
    fig = px.bar(
        selected_materials,
        x='name',
        y='eco_friendly_score',
        color='eco_friendly_score',
        title="Environmental Impact Comparison",
        labels={'eco_friendly_score': 'Eco-Friendly Score (1-10)', 'name': 'Material'},
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Material",
        yaxis_title="Eco-Friendly Score (1-10)",
        xaxis={'categoryorder': 'total descending'}
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_cost_analysis_chart(selected_material_ids, project_area=100):
    """
    Create a horizontal bar chart for cost analysis.
    
    Args:
        selected_material_ids (list): List of selected material IDs
        project_area (float): Project area or quantity
        
    Returns:
        JSON: JSON string for plotly chart
    """
    if not selected_material_ids:
        return None
    
    # Filter materials by selected IDs
    selected_materials = materials_df[materials_df['id'].isin(selected_material_ids)]
    
    # Calculate total cost
    materials_with_cost = selected_materials.copy()
    materials_with_cost['total_cost'] = materials_with_cost['cost_per_unit'] * project_area
    
    # Sort by total cost
    materials_with_cost = materials_with_cost.sort_values(by='total_cost')
    
    # Create figure
    fig = px.bar(
        materials_with_cost,
        x='total_cost',
        y='name',
        orientation='h',
        title=f"Material Cost Comparison (Project Size: {project_area} units)",
        labels={'total_cost': 'Total Cost ($)', 'name': 'Material'},
        color='total_cost',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Total Cost ($)",
        yaxis_title="Material",
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_durability_vs_cost_chart(selected_material_ids=None):
    """
    Create a scatter plot of durability vs cost.
    
    Args:
        selected_material_ids (list): List of selected material IDs
        
    Returns:
        JSON: JSON string for plotly chart
    """
    # Use all materials if none are selected
    if selected_material_ids:
        plot_materials = materials_df[materials_df['id'].isin(selected_material_ids)]
    else:
        plot_materials = materials_df
    
    # Create figure
    fig = px.scatter(
        plot_materials,
        x='cost_per_unit',
        y='durability_years',
        color='type',
        size='strength_mpa',
        hover_name='name',
        text='name',
        title="Durability vs Cost",
        labels={
            'cost_per_unit': 'Cost per Unit ($)',
            'durability_years': 'Durability (years)',
            'type': 'Material Type',
            'strength_mpa': 'Strength (MPa)'
        }
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Cost per Unit ($)",
        yaxis_title="Durability (years)",
        legend_title="Material Type",
        height=500
    )
    
    # Adjust text position
    fig.update_traces(textposition='top center')
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_material_scores_chart(scored_materials):
    """
    Create a horizontal bar chart of material scores.
    
    Args:
        scored_materials (pd.DataFrame): Materials with scores
        
    Returns:
        JSON: JSON string for plotly chart
    """
    if scored_materials.empty:
        return None
    
    # Get the top materials
    top_materials = scored_materials.head(10)
    
    # Sort by total score
    top_materials = top_materials.sort_values(by='total_score')
    
    # Create figure
    fig = px.bar(
        top_materials,
        x='total_score',
        y='name',
        orientation='h',
        title="Material Recommendation Scores",
        labels={'total_score': 'Score (0-10)', 'name': 'Material'},
        color='total_score',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Recommendation Score (0-10)",
        yaxis_title="Material",
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    return render_template('index.html', 
                          applications=APPLICATIONS,
                          material_types=MATERIAL_TYPES)

@app.route('/projects')
def projects_list():
    """List all projects."""
    # Query all projects from the database
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html',
                          projects=all_projects,
                          applications=APPLICATIONS)

@app.route('/projects/new', methods=['POST'])
def create_project():
    """Create a new project."""
    project_name = request.form.get('project_name')
    project_description = request.form.get('project_description', '')
    application = request.form.get('applications')
    
    # Create a new project
    new_project = Project(
        name=project_name,
        description=project_description,
        applications=[application],
        material_types=[],
        min_strength_mpa=0,
        min_durability_years=0,
        fire_resistance_requirement=0,
        water_resistance_requirement=0,
        thermal_requirement=None,
        eco_friendly_requirement=0,
        budget_constraint=None,
        installation_time_constraint=None,
        environmental_conditions={
            'heat': 0,
            'cold': 0,
            'humidity': 0,
            'uv': 0
        }
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    # Redirect to the project specifications page
    return redirect(url_for('project_detail', project_id=new_project.id))

@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    """Show project details and recommendations."""
    # Get the project
    project = Project.query.get_or_404(project_id)
    
    # Get recommendations for this project
    recommendations = Recommendation.query.filter_by(project_id=project_id).order_by(Recommendation.rank).all()
    
    # Get materials for the recommendations
    material_ids = [rec.material_id for rec in recommendations]
    materials = Material.query.filter(Material.id.in_(material_ids)).all()
    
    # Create a dictionary of materials by ID for easier access
    materials_dict = {material.id: material for material in materials}
    
    return render_template('project_detail.html',
                          project=project,
                          recommendations=recommendations,
                          materials_dict=materials_dict)

@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit project details."""
    # Get the project
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        # Update project details
        project.name = request.form.get('project_name')
        project.description = request.form.get('project_description', '')
        project.applications = [request.form.get('applications')]
        
        # Update other project specifications
        project.min_strength_mpa = float(request.form.get('min_strength', 0))
        project.min_durability_years = int(request.form.get('min_durability', 0))
        project.fire_resistance_requirement = float(request.form.get('fire_resistance', 0))
        project.water_resistance_requirement = int(request.form.get('water_resistance', 0))
        project.thermal_requirement = request.form.get('thermal_requirement')
        project.eco_friendly_requirement = int(request.form.get('eco_friendly', 0))
        project.budget_constraint = float(request.form.get('budget')) if request.form.get('budget') else None
        project.installation_time_constraint = request.form.get('installation_time')
        project.environmental_conditions = {
            'heat': int(request.form.get('heat_importance', 0)),
            'cold': int(request.form.get('cold_importance', 0)),
            'humidity': int(request.form.get('humidity_importance', 0)),
            'uv': int(request.form.get('uv_importance', 0))
        }
        
        db.session.commit()
        
        # Recalculate recommendations
        project_specs = {
            'applications': project.applications[0],
            'material_types': project.material_types,
            'min_strength_mpa': project.min_strength_mpa,
            'min_durability_years': project.min_durability_years,
            'fire_resistance_requirement': project.fire_resistance_requirement,
            'water_resistance_requirement': project.water_resistance_requirement,
            'thermal_requirement': project.thermal_requirement,
            'eco_friendly_requirement': project.eco_friendly_requirement,
            'budget_constraint': project.budget_constraint,
            'installation_time_constraint': project.installation_time_constraint,
            'environmental_conditions': project.environmental_conditions
        }
        
        # Get new recommendations
        recommended_materials = recommender.recommend_materials(project_specs, n_recommendations=10)
        
        # Remove old recommendations
        Recommendation.query.filter_by(project_id=project_id).delete()
        
        # Save new recommendations
        for i, (_, material) in enumerate(recommended_materials.iterrows()):
            recommendation = Recommendation(
                project_id=project_id,
                material_id=material['id'],
                score=float(material['total_score']),
                rank=i+1
            )
            db.session.add(recommendation)
        
        db.session.commit()
        
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('edit_project.html',
                          project=project,
                          applications=APPLICATIONS,
                          material_types=MATERIAL_TYPES)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    # Get form data
    project_specs = {
        'applications': request.form.get('applications'),
        'material_types': request.form.getlist('material_types'),
        'min_strength_mpa': float(request.form.get('min_strength', 0)),
        'min_durability_years': float(request.form.get('min_durability', 0)),
        'fire_resistance_requirement': float(request.form.get('fire_resistance', 0)),
        'water_resistance_requirement': float(request.form.get('water_resistance', 0)),
        'thermal_requirement': request.form.get('thermal_requirement'),
        'eco_friendly_requirement': float(request.form.get('eco_friendly', 0)),
        'budget_constraint': float(request.form.get('budget', 0)) if request.form.get('budget') else None,
        'installation_time_constraint': request.form.get('installation_time'),
        'environmental_conditions': {
            'heat': int(request.form.get('heat_importance', 0)),
            'cold': int(request.form.get('cold_importance', 0)),
            'humidity': int(request.form.get('humidity_importance', 0)),
            'uv': int(request.form.get('uv_importance', 0))
        }
    }
    
    # Store project specs in session
    session['project_specs'] = project_specs
    
    # Project name from form or default
    project_name = request.form.get('project_name', 'Unnamed Project')
    project_description = request.form.get('project_description', '')
    
    # Save project to database
    new_project = Project(
        name=project_name,
        description=project_description,
        applications=[project_specs['applications']],
        material_types=project_specs['material_types'],
        min_strength_mpa=project_specs['min_strength_mpa'],
        min_durability_years=project_specs['min_durability_years'],
        fire_resistance_requirement=project_specs['fire_resistance_requirement'],
        water_resistance_requirement=project_specs['water_resistance_requirement'],
        thermal_requirement=project_specs['thermal_requirement'],
        eco_friendly_requirement=project_specs['eco_friendly_requirement'],
        budget_constraint=project_specs['budget_constraint'],
        installation_time_constraint=project_specs['installation_time_constraint'],
        environmental_conditions=project_specs['environmental_conditions']
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    # Store project ID in session
    session['project_id'] = new_project.id
    
    # Get recommendations
    recommended_materials = recommender.recommend_materials(project_specs, n_recommendations=10)
    
    # Save recommendations to database
    for i, (_, material) in enumerate(recommended_materials.iterrows()):
        recommendation = Recommendation(
            project_id=new_project.id,
            material_id=material['id'],
            score=float(material['total_score']),
            rank=i+1
        )
        db.session.add(recommendation)
    
    db.session.commit()
    
    # Convert DataFrame to dict for JSON serialization
    recommended_materials_dict = recommended_materials.reset_index().to_dict(orient='records')
    
    # Store recommendations in session
    session['recommended_materials'] = recommended_materials_dict
    
    # Create scores chart
    scores_chart = create_material_scores_chart(recommended_materials)
    
    return jsonify({
        'success': True,
        'materials': recommended_materials_dict,
        'scores_chart': scores_chart,
        'project_id': new_project.id
    })

@app.route('/get_durability_cost_chart')
def get_durability_cost_chart():
    """Get durability vs cost chart for all materials."""
    chart_json = create_durability_vs_cost_chart()
    return jsonify(chart_json)

@app.route('/update_cost_chart')
def update_cost_chart():
    """Update cost chart with new project area."""
    project_area = float(request.args.get('project_area', 100))
    
    if 'comparisons' not in session or not session['comparisons']:
        return jsonify({})
    
    chart_json = create_cost_analysis_chart(session['comparisons'], project_area)
    return jsonify(chart_json)

@app.route('/material/<int:material_id>')
def material_detail(material_id):
    material = materials_df[materials_df['id'] == material_id].iloc[0].to_dict()
    supplier_id = material['supplier_id']
    supplier = suppliers_df[suppliers_df['supplier_id'] == supplier_id].iloc[0].to_dict()
    
    # Add this material to comparisons if not already there
    if 'comparisons' not in session:
        session['comparisons'] = []
    
    if material_id not in session['comparisons']:
        session['comparisons'].append(material_id)
    
    # Get similar materials
    similar_materials = recommender.get_similar_materials(material_id, n_neighbors=3)
    similar_materials_data = materials_df[materials_df['id'].isin(similar_materials)]
    similar_materials_dict = similar_materials_data.reset_index().to_dict(orient='records')
    
    return render_template('material_detail.html', 
                          material=material,
                          supplier=supplier,
                          similar_materials=similar_materials_dict)

@app.route('/comparisons')
def comparisons():
    if 'comparisons' not in session or not session['comparisons']:
        return render_template('comparisons.html', 
                              materials=[],
                              comparison_chart=None,
                              environmental_chart=None,
                              cost_chart=None)
    
    selected_material_ids = session['comparisons']
    selected_materials = materials_df[materials_df['id'].isin(selected_material_ids)]
    
    # Create comparison charts
    comparison_chart = create_material_comparison_chart(selected_material_ids)
    environmental_chart = create_environmental_impact_chart(selected_material_ids)
    cost_chart = create_cost_analysis_chart(selected_material_ids)
    
    # Get supplier information
    supplier_ids = selected_materials['supplier_id'].unique().tolist()
    suppliers = suppliers_df[suppliers_df['supplier_id'].isin(supplier_ids)]
    
    return render_template('comparisons.html',
                          materials=selected_materials.to_dict(orient='records'),
                          suppliers=suppliers.to_dict(orient='records'),
                          comparison_chart=comparison_chart,
                          environmental_chart=environmental_chart,
                          cost_chart=cost_chart)

@app.route('/add_to_comparison/<int:material_id>')
def add_to_comparison(material_id):
    if 'comparisons' not in session:
        session['comparisons'] = []
    
    if material_id not in session['comparisons']:
        session['comparisons'].append(material_id)
    
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_comparison/<int:material_id>')
def remove_from_comparison(material_id):
    if 'comparisons' in session and material_id in session['comparisons']:
        session['comparisons'].remove(material_id)
    
    return redirect(request.referrer or url_for('comparisons'))

@app.route('/clear_comparisons')
def clear_comparisons():
    if 'comparisons' in session:
        session['comparisons'] = []
    
    return redirect(url_for('comparisons'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)