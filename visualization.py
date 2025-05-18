"""
Visualization module for the construction material recommendation system.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def visualize_material_comparison(materials_df, selected_material_ids):
    """
    Create a radar chart comparing material properties.

    Args:
        materials_df (pd.DataFrame): Materials database
        selected_material_ids (list): List of selected material IDs

    Returns:
        go.Figure: Plotly figure object
    """
    if not selected_material_ids:
        return None

    # Filter the materials by selected IDs
    selected_materials = materials_df[materials_df["id"].isin(selected_material_ids)]

    # Properties to be compared
    properties = [
        "strength_mpa",
        "durability_years",
        "fire_resistance_hours",
        "water_resistance",
        "eco_friendly_score",
        "cost_per_unit",
        "maintenance_requirement",
        "installation_complexity",
    ]

    # Short display names for the properties
    property_names = [
        "Strength",
        "Durability",
        "Fire Resistance",
        "Water Resistance",
        "Eco-Friendly",
        "Cost (inv)",
        "Maintenance (inv)",
        "Installation (inv)",
    ]

    # Create figure
    fig = go.Figure()

    # Normalize properties for radar chart
    normalized_data = {}
    for prop in properties:
        max_val = max(selected_materials[prop].max(), 1)  # Avoid division by zero

        # For cost and complexity, lower is better, so we invert
        if prop in [
            "cost_per_unit",
            "maintenance_requirement",
            "installation_complexity",
        ]:
            normalized_data[prop] = 1 - (selected_materials[prop] / max_val)
        else:
            normalized_data[prop] = selected_materials[prop] / max_val

    # Add traces for each material
    for _, material in selected_materials.iterrows():
        values = [normalized_data[prop].loc[material.name] for prop in properties]
        values.append(values[0])  # Close the loop

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=property_names + [property_names[0]],  # Close the loop
                fill="toself",
                name=material["name"],
            )
        )

    # Update layout
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="Material Properties Comparison",
    )

    return fig


def visualize_cost_analysis(materials_df, selected_material_ids, project_area=100):
    """
    Create a horizontal bar chart for cost analysis.

    Args:
        materials_df (pd.DataFrame): Materials database
        selected_material_ids (list): List of selected material IDs
        project_area (float): Project area or quantity

    Returns:
        go.Figure: Plotly figure object
    """
    if not selected_material_ids:
        return None

    # Filter materials by selected IDs
    selected_materials = materials_df[materials_df["id"].isin(selected_material_ids)]

    # Calculate total cost
    materials_with_cost = selected_materials.copy()
    materials_with_cost["total_cost"] = (
        materials_with_cost["cost_per_unit"] * project_area
    )

    # Sort by total cost
    materials_with_cost = materials_with_cost.sort_values(by="total_cost")

    # Create figure
    fig = px.bar(
        materials_with_cost,
        x="total_cost",
        y="name",
        orientation="h",
        title=f"Material Cost Comparison (Project Size: {project_area} units)",
        labels={"total_cost": "Total Cost ($)", "name": "Material"},
        color="total_cost",
        color_continuous_scale="Viridis",
    )

    # Update layout
    fig.update_layout(xaxis_title="Total Cost ($)", yaxis_title="Material", height=400)

    return fig


def visualize_durability_vs_cost(materials_df, selected_material_ids=None):
    """
    Create a scatter plot of durability vs cost.

    Args:
        materials_df (pd.DataFrame): Materials database
        selected_material_ids (list): List of selected material IDs

    Returns:
        go.Figure: Plotly figure object
    """
    # Use all materials if none are selected
    if selected_material_ids:
        plot_materials = materials_df[materials_df["id"].isin(selected_material_ids)]
    else:
        plot_materials = materials_df

    # Create figure
    fig = px.scatter(
        plot_materials,
        x="cost_per_unit",
        y="durability_years",
        color="type",
        size="strength_mpa",
        hover_name="name",
        text="name",
        title="Durability vs Cost",
        labels={
            "cost_per_unit": "Cost per Unit ($)",
            "durability_years": "Durability (years)",
            "type": "Material Type",
            "strength_mpa": "Strength (MPa)",
        },
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Cost per Unit ($)",
        yaxis_title="Durability (years)",
        legend_title="Material Type",
        height=500,
    )

    # Adjust text position
    fig.update_traces(textposition="top center")

    return fig


def visualize_environmental_impact(materials_df, selected_material_ids):
    """
    Create a bar chart of eco-friendly scores.

    Args:
        materials_df (pd.DataFrame): Materials database
        selected_material_ids (list): List of selected material IDs

    Returns:
        go.Figure: Plotly figure object
    """
    if not selected_material_ids:
        return None

    # Filter materials by selected IDs
    selected_materials = materials_df[materials_df["id"].isin(selected_material_ids)]

    # Sort by eco-friendly score
    selected_materials = selected_materials.sort_values(
        by="eco_friendly_score", ascending=False
    )

    # Create figure
    fig = px.bar(
        selected_materials,
        x="name",
        y="eco_friendly_score",
        color="eco_friendly_score",
        title="Environmental Impact Comparison",
        labels={"eco_friendly_score": "Eco-Friendly Score (1-10)", "name": "Material"},
        color_continuous_scale="Viridis",
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Material",
        yaxis_title="Eco-Friendly Score (1-10)",
        xaxis={"categoryorder": "total descending"},
    )

    return fig


def visualize_weather_resistance(materials_df, selected_material_ids):
    """
    Create a heatmap of weather resistance properties.

    Args:
        materials_df (pd.DataFrame): Materials database
        selected_material_ids (list): List of selected material IDs

    Returns:
        go.Figure: Plotly figure object
    """
    if not selected_material_ids:
        return None

    # Filter materials by selected IDs
    selected_materials = materials_df[materials_df["id"].isin(selected_material_ids)]

    # Extract weather resistance properties
    weather_data = []
    materials_names = []

    for _, material in selected_materials.iterrows():
        materials_names.append(material["name"])
        weather_data.append(
            [
                material["weather_resistance"].get("heat", 0),
                material["weather_resistance"].get("cold", 0),
                material["weather_resistance"].get("humidity", 0),
                material["weather_resistance"].get("uv", 0),
            ]
        )

    # Create heatmap
    fig = px.imshow(
        weather_data,
        labels=dict(x="Weather Condition", y="Material", color="Resistance Score"),
        x=["Heat", "Cold", "Humidity", "UV"],
        y=materials_names,
        color_continuous_scale="Viridis",
        title="Weather Resistance Comparison",
    )

    # Add text annotations
    for i in range(len(materials_names)):
        for j in range(4):  # 4 weather conditions
            fig.add_annotation(
                x=j,
                y=i,
                text=str(weather_data[i][j]),
                showarrow=False,
                font=dict(color="white" if weather_data[i][j] < 5 else "black"),
            )

    return fig


def visualize_material_scores(scored_materials):
    """
    Create a horizontal bar chart of material scores.

    Args:
        scored_materials (pd.DataFrame): Materials with scores

    Returns:
        go.Figure: Plotly figure object
    """
    if scored_materials.empty:
        return None

    # Get the top materials
    top_materials = scored_materials.head(10)

    # Sort by total score
    top_materials = top_materials.sort_values(by="total_score")

    # Create figure
    fig = px.bar(
        top_materials,
        x="total_score",
        y="name",
        orientation="h",
        title="Material Recommendation Scores",
        labels={"total_score": "Score (0-10)", "name": "Material"},
        color="total_score",
        color_continuous_scale="Viridis",
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Recommendation Score (0-10)", yaxis_title="Material", height=400
    )

    return fig


def visualize_supplier_comparison(suppliers_df, supplier_ids):
    """
    Create a figure comparing supplier metrics.

    Args:
        suppliers_df (pd.DataFrame): Suppliers database
        supplier_ids (list): List of supplier IDs

    Returns:
        go.Figure: Plotly figure object
    """
    if not supplier_ids:
        return None

    # Filter suppliers by IDs
    selected_suppliers = suppliers_df[suppliers_df["supplier_id"].isin(supplier_ids)]

    # Create subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Delivery Time", "Reliability Score"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
    )

    # Add delivery time bars
    fig.add_trace(
        go.Bar(
            x=selected_suppliers["name"],
            y=selected_suppliers["delivery_time_days"],
            name="Delivery Time (days)",
        ),
        row=1,
        col=1,
    )

    # Add reliability score bars
    fig.add_trace(
        go.Bar(
            x=selected_suppliers["name"],
            y=selected_suppliers["reliability_score"],
            name="Reliability Score (1-10)",
        ),
        row=1,
        col=2,
    )

    # Update layout
    fig.update_layout(title_text="Supplier Comparison", height=400)

    return fig
