"""
Data utility functions for the construction material recommendation system.
This module contains functions for data processing and feature extraction.
"""

import pandas as pd
import numpy as np
from material_data import get_material_properties, get_weather_properties


def preprocess_material_data(materials_df):
    """
    Preprocess material data for machine learning.

    Args:
        materials_df (pd.DataFrame): Materials database

    Returns:
        pd.DataFrame: Processed feature matrix for materials
    """
    # Extract the numerical properties as features
    features = get_material_properties()
    X = materials_df[features].copy()

    # Extract weather resistance scores and add them as features
    weather_props = get_weather_properties()
    for prop in weather_props:
        X[f"weather_{prop}"] = materials_df["weather_resistance"].apply(
            lambda x: x.get(prop, 0)
        )

    # Create dummy variables for material type and application
    type_dummies = pd.get_dummies(materials_df["type"], prefix="type")

    # For applications (which is a list column), we need to process differently
    app_dummies = pd.DataFrame()
    for app in set(app for apps in materials_df["applications"] for app in apps):
        app_dummies[f"app_{app}"] = materials_df["applications"].apply(
            lambda x: 1 if app in x else 0
        )

    # Combine all features
    X = pd.concat([X, type_dummies, app_dummies], axis=1)

    return X


def extract_project_features(project_specs):
    """
    Extract features from project specifications.

    Args:
        project_specs (dict): Project specifications

    Returns:
        pd.DataFrame: Processed feature matrix for the project
    """
    # Create a DataFrame with a single row for the project
    project_df = pd.DataFrame([project_specs])

    # Initialize the feature vector
    features = {}

    # Process the application
    applications = project_specs.get("applications", [])
    if not isinstance(applications, list):
        applications = [applications]

    # Process material type preferences
    material_types = project_specs.get("material_types", [])
    if not isinstance(material_types, list):
        material_types = [material_types]

    # Process numerical requirements for the objective
    numerical_features = [
        "min_strength_mpa",
        "min_durability_years",
        "fire_resistance_requirement",
        "water_resistance_requirement",
        "thermal_requirement",
        "eco_friendly_requirement",
        "budget_constraint",
        "installation_time_constraint",
    ]

    for feature in numerical_features:
        if feature in project_specs:
            features[feature] = project_specs[feature]

    # Process environmental conditions

    env_conditions = project_specs.get("environmental_conditions", {})
    if env_conditions:
        for condition, value in env_conditions.items():
            features[f"env_{condition}"] = value

    # Converting into DataFrame

    project_features = pd.DataFrame([features])

    return project_features


def calculate_material_scores(materials_df, project_specs):
    """
    Calculate scores for each material based on project specifications.

    Args:
        materials_df (pd.DataFrame): Materials database
        project_specs (dict): Project specifications

    Returns:
        pd.DataFrame: DataFrame with material scores
    """
    # Create a copy of the materials dataframe to add scores
    scored_materials = materials_df.copy()

    # Initialize score column
    scored_materials["total_score"] = 0

    # Weight factors for different aspects
    weights = {
        "application_match": 5,
        "strength": 3,
        "durability": 3,
        "fire_resistance": 2,
        "water_resistance": 2,
        "thermal": 2,
        "eco_friendly": 2,
        "cost": 4,
        "availability": 3,
        "maintenance": 2,
        "weather": 3,
        "installation": 2,
    }

    # Score for application match
    requested_applications = project_specs.get("applications", [])
    if not isinstance(requested_applications, list):
        requested_applications = [requested_applications]

    scored_materials["application_score"] = (
        scored_materials["applications"].apply(
            lambda x: sum(1 for app in requested_applications if app in x)
            / max(1, len(requested_applications))
        )
        * 10
    )
    scored_materials["total_score"] += (
        scored_materials["application_score"] * weights["application_match"]
    )

    # Score for material type preference
    preferred_types = project_specs.get("material_types", [])
    if preferred_types:
        if not isinstance(preferred_types, list):
            preferred_types = [preferred_types]

        scored_materials["type_score"] = scored_materials["type"].apply(
            lambda x: 10 if x in preferred_types else 5
        )
        scored_materials["total_score"] += (
            scored_materials["type_score"] * weights["strength"]
        )

    # Score for strength
    min_strength = project_specs.get("min_strength_mpa", 0)
    if min_strength > 0:
        scored_materials["strength_score"] = np.where(
            scored_materials["strength_mpa"] >= min_strength,
            10,
            10 * (scored_materials["strength_mpa"] / min_strength),
        )
        scored_materials["total_score"] += (
            scored_materials["strength_score"] * weights["strength"]
        )

    # Score for durability
    min_durability = project_specs.get("min_durability_years", 0)
    if min_durability > 0:
        scored_materials["durability_score"] = np.where(
            scored_materials["durability_years"] >= min_durability,
            10,
            10 * (scored_materials["durability_years"] / min_durability),
        )
        scored_materials["total_score"] += (
            scored_materials["durability_score"] * weights["durability"]
        )

    # Score for fire resistance
    fire_req = project_specs.get("fire_resistance_requirement", 0)
    if fire_req > 0:
        scored_materials["fire_score"] = np.where(
            scored_materials["fire_resistance_hours"] >= fire_req,
            10,
            10 * (scored_materials["fire_resistance_hours"] / fire_req),
        )
        scored_materials["total_score"] += (
            scored_materials["fire_score"] * weights["fire_resistance"]
        )

    # Score for water resistance
    water_req = project_specs.get("water_resistance_requirement", 0)
    if water_req > 0:
        scored_materials["water_score"] = np.where(
            scored_materials["water_resistance"] >= water_req,
            10,
            10 * (scored_materials["water_resistance"] / water_req),
        )
        scored_materials["total_score"] += (
            scored_materials["water_score"] * weights["water_resistance"]
        )

    # Score for thermal properties
    thermal_req = project_specs.get("thermal_requirement", None)
    if thermal_req is not None:
        if thermal_req == "low":  # Good insulation
            scored_materials["thermal_score"] = 10 - (
                scored_materials["thermal_conductivity"] / 10
            )
        else:  # High conductivity
            scored_materials["thermal_score"] = (
                scored_materials["thermal_conductivity"] / 10
            )

        scored_materials["thermal_score"] = scored_materials["thermal_score"].clip(
            0, 10
        )
        scored_materials["total_score"] += (
            scored_materials["thermal_score"] * weights["thermal"]
        )

    # Score for eco-friendliness
    eco_req = project_specs.get("eco_friendly_requirement", 0)
    if eco_req > 0:
        scored_materials["eco_score"] = np.where(
            scored_materials["eco_friendly_score"] >= eco_req,
            10,
            10 * (scored_materials["eco_friendly_score"] / eco_req),
        )
        scored_materials["total_score"] += (
            scored_materials["eco_score"] * weights["eco_friendly"]
        )

    # Score for cost (lower is better)
    budget = project_specs.get("budget_constraint", None)
    if budget is not None:
        scored_materials["cost_score"] = np.where(
            scored_materials["cost_per_unit"] <= budget,
            10,
            10 * (budget / scored_materials["cost_per_unit"]),
        )
        scored_materials["total_score"] += (
            scored_materials["cost_score"] * weights["cost"]
        )

    # Score for weather resistance
    env_conditions = project_specs.get("environmental_conditions", {})
    if env_conditions:
        weather_score = 0
        count = 0

        for condition, importance in env_conditions.items():
            if importance > 0 and condition in ["heat", "cold", "humidity", "uv"]:
                weather_score += (
                    scored_materials["weather_resistance"].apply(
                        lambda x: x.get(condition, 5)
                    )
                    * importance
                    / 10
                )
                count += importance / 10

        if count > 0:
            scored_materials["weather_score"] = weather_score / count
            scored_materials["total_score"] += (
                scored_materials["weather_score"] * weights["weather"]
            )

    # Score for installation complexity (lower is better)
    install_constraint = project_specs.get("installation_time_constraint", None)
    if install_constraint is not None:
        if install_constraint == "low":
            scored_materials["install_score"] = (
                10 - scored_materials["installation_complexity"]
            )
        else:
            scored_materials["install_score"] = scored_materials[
                "installation_complexity"
            ]

        scored_materials["total_score"] += (
            scored_materials["install_score"] * weights["installation"]
        )

    # Normalize the total score
    total_weight = sum(w for k, w in weights.items())
    scored_materials["total_score"] = (
        scored_materials["total_score"] / total_weight * 10
    )

    # Sort by total score in descending order
    scored_materials = scored_materials.sort_values(by="total_score", ascending=False)

    return scored_materials


def filter_materials_by_application(materials_df, application):
    """
    Filter materials by application.

    Args:
        materials_df (pd.DataFrame): Materials database
        application (str): Requested application

    Returns:
        pd.DataFrame: Filtered materials
    """
    return materials_df[materials_df["applications"].apply(lambda x: application in x)]
