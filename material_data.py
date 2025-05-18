"""
Material data module for the construction material recommendation system.
This module contains the material database and related utility functions.
"""

import pandas as pd
import numpy as np
import os
import json
from db_utils import get_material_from_db, get_supplier_from_db

# Define material properties and their possible values
MATERIAL_TYPES = [
    "Concrete",
    "Steel",
    "Wood",
    "Brick",
    "Glass",
    "Aluminum",
    "Stone",
    "Ceramic",
    "Plastic",
    "Composite",
]

APPLICATIONS = [
    "Foundation",
    "Structural",
    "Roofing",
    "Flooring",
    "Wall",
    "Insulation",
    "Facade",
    "Windows",
    "Doors",
    "Interior Finishing",
]


def generate_material_database():
    """
    Generate a database of construction materials with their properties.

    Returns:
        pd.DataFrame: DataFrame containing material information
    """
    try:
        # First, try to get materials from the database
        materials_df = get_material_from_db()
        if not materials_df.empty:
            return materials_df
    except Exception as e:
        print(f"Error retrieving materials from database: {e}")
        print("Using fallback material data...")

    # Fallback to local data if database is unavailable
    materials = []

    # Concrete types
    materials.append(
        {
            "id": 1,
            "name": "Standard Portland Cement Concrete",
            "type": "Concrete",
            "applications": ["Foundation", "Structural", "Flooring"],
            "strength_mpa": 25.0,
            "durability_years": 50,
            "thermal_conductivity": 1.7,  # W/(m·K)
            "fire_resistance_hours": 4,
            "water_resistance": 8,  # Scale 1-10
            "eco_friendly_score": 4,  # Scale 1-10
            "cost_per_unit": 110.0,  # USD per cubic meter
            "availability": 9,  # Scale 1-10
            "maintenance_requirement": 3,  # Scale 1-10
            "weather_resistance": {"heat": 9, "cold": 7, "humidity": 8, "uv": 8},
            "installation_complexity": 5,  # Scale 1-10
            "supplier_id": "SUP001",
        }
    )

    # Add more materials...
    # (Same as before - included just the first one for brevity)

    # Steel types
    materials.append(
        {
            "id": 3,
            "name": "Structural Steel (A36)",
            "type": "Steel",
            "applications": ["Structural"],
            "strength_mpa": 400.0,
            "durability_years": 60,
            "thermal_conductivity": 45.0,
            "fire_resistance_hours": 0.5,
            "water_resistance": 4,
            "eco_friendly_score": 6,
            "cost_per_unit": 2000.0,
            "availability": 8,
            "maintenance_requirement": 5,
            "weather_resistance": {"heat": 6, "cold": 8, "humidity": 3, "uv": 7},
            "installation_complexity": 7,
            "supplier_id": "SUP003",
        }
    )

    # Wood types
    materials.append(
        {
            "id": 5,
            "name": "Douglas Fir Lumber",
            "type": "Wood",
            "applications": ["Structural", "Flooring"],
            "strength_mpa": 85.0,
            "durability_years": 25,
            "thermal_conductivity": 0.12,
            "fire_resistance_hours": 0.75,
            "water_resistance": 3,
            "eco_friendly_score": 8,
            "cost_per_unit": 600.0,
            "availability": 7,
            "maintenance_requirement": 7,
            "weather_resistance": {"heat": 5, "cold": 7, "humidity": 4, "uv": 3},
            "installation_complexity": 4,
            "supplier_id": "SUP005",
        }
    )

    # Brick types
    materials.append(
        {
            "id": 7,
            "name": "Clay Brick",
            "type": "Brick",
            "applications": ["Wall", "Facade"],
            "strength_mpa": 15.0,
            "durability_years": 100,
            "thermal_conductivity": 0.6,
            "fire_resistance_hours": 6,
            "water_resistance": 7,
            "eco_friendly_score": 7,
            "cost_per_unit": 400.0,
            "availability": 9,
            "maintenance_requirement": 2,
            "weather_resistance": {"heat": 9, "cold": 8, "humidity": 7, "uv": 9},
            "installation_complexity": 6,
            "supplier_id": "SUP007",
        }
    )

    # Glass types
    materials.append(
        {
            "id": 8,
            "name": "Tempered Glass",
            "type": "Glass",
            "applications": ["Windows", "Doors", "Facade"],
            "strength_mpa": 100.0,
            "durability_years": 30,
            "thermal_conductivity": 1.0,
            "fire_resistance_hours": 0.25,
            "water_resistance": 10,
            "eco_friendly_score": 6,
            "cost_per_unit": 70.0,
            "availability": 8,
            "maintenance_requirement": 4,
            "weather_resistance": {"heat": 7, "cold": 7, "humidity": 10, "uv": 7},
            "installation_complexity": 7,
            "supplier_id": "SUP008",
        }
    )

    # Aluminum types
    materials.append(
        {
            "id": 10,
            "name": "Aluminum Alloy 6061",
            "type": "Aluminum",
            "applications": ["Structural", "Facade", "Windows", "Doors"],
            "strength_mpa": 310.0,
            "durability_years": 40,
            "thermal_conductivity": 167.0,
            "fire_resistance_hours": 0.1,
            "water_resistance": 8,
            "eco_friendly_score": 8,
            "cost_per_unit": 3000.0,
            "availability": 8,
            "maintenance_requirement": 3,
            "weather_resistance": {"heat": 7, "cold": 9, "humidity": 8, "uv": 9},
            "installation_complexity": 5,
            "supplier_id": "SUP010",
        }
    )

    # Stone types
    materials.append(
        {
            "id": 11,
            "name": "Granite",
            "type": "Stone",
            "applications": ["Flooring", "Facade", "Interior Finishing"],
            "strength_mpa": 170.0,
            "durability_years": 100,
            "thermal_conductivity": 2.8,
            "fire_resistance_hours": 6,
            "water_resistance": 8,
            "eco_friendly_score": 6,
            "cost_per_unit": 200.0,
            "availability": 6,
            "maintenance_requirement": 3,
            "weather_resistance": {"heat": 9, "cold": 9, "humidity": 8, "uv": 9},
            "installation_complexity": 7,
            "supplier_id": "SUP011",
        }
    )

    # Ceramic types
    materials.append(
        {
            "id": 12,
            "name": "Porcelain Tile",
            "type": "Ceramic",
            "applications": ["Flooring", "Wall", "Interior Finishing"],
            "strength_mpa": 35.0,
            "durability_years": 50,
            "thermal_conductivity": 1.5,
            "fire_resistance_hours": 5,
            "water_resistance": 9,
            "eco_friendly_score": 6,
            "cost_per_unit": 30.0,
            "availability": 9,
            "maintenance_requirement": 2,
            "weather_resistance": {"heat": 9, "cold": 8, "humidity": 9, "uv": 9},
            "installation_complexity": 5,
            "supplier_id": "SUP012",
        }
    )

    # Plastic types
    materials.append(
        {
            "id": 13,
            "name": "PVC",
            "type": "Plastic",
            "applications": ["Doors", "Windows", "Interior Finishing"],
            "strength_mpa": 55.0,
            "durability_years": 35,
            "thermal_conductivity": 0.19,
            "fire_resistance_hours": 0.2,
            "water_resistance": 10,
            "eco_friendly_score": 3,
            "cost_per_unit": 25.0,
            "availability": 10,
            "maintenance_requirement": 2,
            "weather_resistance": {"heat": 5, "cold": 8, "humidity": 10, "uv": 4},
            "installation_complexity": 3,
            "supplier_id": "SUP013",
        }
    )

    # Create a DataFrame from the materials list
    df = pd.DataFrame(materials)

    return df


def generate_supplier_database():
    """
    Generate a database of suppliers with their information.

    Returns:
        pd.DataFrame: DataFrame containing supplier information
    """
    try:
        # First, try to get suppliers from the database
        suppliers_df = get_supplier_from_db()
        if not suppliers_df.empty:
            return suppliers_df
    except Exception as e:
        print(f"Error retrieving suppliers from database: {e}")
        print("Using fallback supplier data...")

    # Fallback to local data if database is unavailable
    suppliers = [
        {
            "supplier_id": "SUP001",
            "name": "ConcreteWorks Inc.",
            "location": "Chicago, IL",
            "delivery_time_days": 3,
            "reliability_score": 8,
            "price_level": "Medium",
            "contact": "sales@concreteworks.com",
        },
        {
            "supplier_id": "SUP002",
            "name": "Premium Concrete Solutions",
            "location": "Denver, CO",
            "delivery_time_days": 5,
            "reliability_score": 9,
            "price_level": "High",
            "contact": "orders@premiumconcrete.com",
        },
        {
            "supplier_id": "SUP003",
            "name": "American Steel Corp",
            "location": "Pittsburgh, PA",
            "delivery_time_days": 7,
            "reliability_score": 9,
            "price_level": "Medium",
            "contact": "sales@americansteel.com",
        },
        {
            "supplier_id": "SUP004",
            "name": "Superior Stainless",
            "location": "Cleveland, OH",
            "delivery_time_days": 10,
            "reliability_score": 8,
            "price_level": "High",
            "contact": "orders@superiorstainless.com",
        },
        {
            "supplier_id": "SUP005",
            "name": "Northwest Timber",
            "location": "Seattle, WA",
            "delivery_time_days": 5,
            "reliability_score": 7,
            "price_level": "Medium",
            "contact": "info@nwtimber.com",
        },
        {
            "supplier_id": "SUP006",
            "name": "Southern Pine Products",
            "location": "Atlanta, GA",
            "delivery_time_days": 4,
            "reliability_score": 8,
            "price_level": "Medium",
            "contact": "sales@southernpine.com",
        },
        {
            "supplier_id": "SUP007",
            "name": "Classic Brick Co.",
            "location": "Philadelphia, PA",
            "delivery_time_days": 6,
            "reliability_score": 9,
            "price_level": "Medium",
            "contact": "orders@classicbrick.com",
        },
        {
            "supplier_id": "SUP008",
            "name": "Crystal Glass Works",
            "location": "Minneapolis, MN",
            "delivery_time_days": 8,
            "reliability_score": 7,
            "price_level": "Medium",
            "contact": "sales@crystalglass.com",
        },
        {
            "supplier_id": "SUP009",
            "name": "Advanced Glass Technologies",
            "location": "San Francisco, CA",
            "delivery_time_days": 12,
            "reliability_score": 9,
            "price_level": "High",
            "contact": "info@advancedglass.com",
        },
        {
            "supplier_id": "SUP010",
            "name": "Aluminum Systems Inc.",
            "location": "Houston, TX",
            "delivery_time_days": 6,
            "reliability_score": 8,
            "price_level": "Medium",
            "contact": "orders@aluminumsystems.com",
        },
        {
            "supplier_id": "SUP011",
            "name": "Granite Mountain Quarries",
            "location": "Barre, VT",
            "delivery_time_days": 15,
            "reliability_score": 9,
            "price_level": "High",
            "contact": "sales@granitemountain.com",
        },
        {
            "supplier_id": "SUP012",
            "name": "Ceramic Tile Distributors",
            "location": "Miami, FL",
            "delivery_time_days": 5,
            "reliability_score": 7,
            "price_level": "Low",
            "contact": "orders@ceramictile.com",
        },
        {
            "supplier_id": "SUP013",
            "name": "Modern Plastics Corp",
            "location": "Dallas, TX",
            "delivery_time_days": 4,
            "reliability_score": 8,
            "price_level": "Low",
            "contact": "sales@modernplastics.com",
        },
        {
            "supplier_id": "SUP014",
            "name": "Composite Building Products",
            "location": "Portland, OR",
            "delivery_time_days": 7,
            "reliability_score": 8,
            "price_level": "Medium",
            "contact": "info@compositebuilding.com",
        },
        {
            "supplier_id": "SUP015",
            "name": "Eco Composite Materials",
            "location": "Austin, TX",
            "delivery_time_days": 9,
            "reliability_score": 7,
            "price_level": "Medium",
            "contact": "sales@ecocomposite.com",
        },
    ]

    return pd.DataFrame(suppliers)


# get the material properties


def get_material_properties():
    """
    Get a list of material properties for feature extraction.

    Returns:
        list: List of material properties
    """
    properties = [
        "strength_mpa",
        "durability_years",
        "thermal_conductivity",
        "fire_resistance_hours",
        "water_resistance",
        "eco_friendly_score",
        "cost_per_unit",
        "availability",
        "maintenance_requirement",
        "installation_complexity",
    ]
    return properties


def get_weather_properties():
    """
    Get a list of weather resistance properties.

    Returns:
        list: List of weather resistance properties
    """
    properties = ["heat", "cold", "humidity", "uv"]
    return properties


def get_material_by_id(material_id, materials_df):
    """
    Get material information by ID.

    Args:
        material_id (int): Material ID
        materials_df (pd.DataFrame): Materials database

    Returns:
        dict: Material information
    """
    material = materials_df[materials_df["id"] == material_id].iloc[0].to_dict()
    return material


def get_supplier_by_id(supplier_id, suppliers_df):
    """
    Get supplier information by ID.

    Args:
        supplier_id (str): Supplier ID
        suppliers_df (pd.DataFrame): Suppliers database

    Returns:
        dict: Supplier information
    """
    supplier = (
        suppliers_df[suppliers_df["supplier_id"] == supplier_id].iloc[0].to_dict()
    )
    return supplier
