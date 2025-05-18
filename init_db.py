"""
Database initialization script for the construction material recommendation system.
This script creates the database tables and populates them with initial data.
"""

import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from db_utils import check_and_create_tables
from material_data import generate_material_database, generate_supplier_database
from dotenv import load_dotenv

load_dotenv()


def init_database():
    """Initialize the database with tables and initial data."""
    print("Initializing database...")

    # Check and create tables
    check_and_create_tables()

    # Get database URL from environment
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable not set.")
        return

    # Create engine
    engine = create_engine(DATABASE_URL)

    try:
        # Check if materials table has data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM materials"))
            materials_count = result.scalar()

            if materials_count == 0:
                # Get material data
                materials_df = generate_material_database()

                # Insert materials into database
                insert_materials(materials_df, engine)

                print(f"Added {len(materials_df)} materials to the database.")
            else:
                print(
                    f"Materials table already has {materials_count} records. Skipping material data insertion."
                )

        # Check if suppliers table has data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM suppliers"))
            suppliers_count = result.scalar()

            if suppliers_count == 0:
                # Get supplier data
                suppliers_df = generate_supplier_database()

                # Insert suppliers into database
                insert_suppliers(suppliers_df, engine)

                print(f"Added {len(suppliers_df)} suppliers to the database.")
            else:
                print(
                    f"Suppliers table already has {suppliers_count} records. Skipping supplier data insertion."
                )

        print("Database initialization complete.")
    except Exception as e:
        print(f"Error initializing database: {e}")


def insert_materials(materials_df, engine):
    """
    Insert materials into the database.

    Args:
        materials_df (pd.DataFrame): Materials data
        engine: SQLAlchemy engine
    """
    with engine.connect() as conn:
        for _, material in materials_df.iterrows():
            # Convert weather_resistance to JSON string
            weather_resistance = json.dumps(material["weather_resistance"])

            # Convert applications to JSON string
            applications = json.dumps(material["applications"])

            # Insert material
            conn.execute(
                text(
                    """
                INSERT INTO materials (
                    id, name, type, applications, strength_mpa, durability_years,
                    thermal_conductivity, fire_resistance_hours, water_resistance,
                    eco_friendly_score, cost_per_unit, availability,
                    maintenance_requirement, weather_resistance, installation_complexity,
                    supplier_id
                ) VALUES (
                    :id, :name, :type, :applications, :strength_mpa, :durability_years,
                    :thermal_conductivity, :fire_resistance_hours, :water_resistance,
                    :eco_friendly_score, :cost_per_unit, :availability,
                    :maintenance_requirement, :weather_resistance, :installation_complexity,
                    :supplier_id
                )
                ON CONFLICT (id) DO NOTHING
                """
                ),
                {
                    "id": int(material["id"]),
                    "name": material["name"],
                    "type": material["type"],
                    "applications": applications,
                    "strength_mpa": float(material["strength_mpa"]),
                    "durability_years": int(material["durability_years"]),
                    "thermal_conductivity": float(material["thermal_conductivity"]),
                    "fire_resistance_hours": float(material["fire_resistance_hours"]),
                    "water_resistance": int(material["water_resistance"]),
                    "eco_friendly_score": int(material["eco_friendly_score"]),
                    "cost_per_unit": float(material["cost_per_unit"]),
                    "availability": int(material["availability"]),
                    "maintenance_requirement": int(material["maintenance_requirement"]),
                    "weather_resistance": weather_resistance,
                    "installation_complexity": int(material["installation_complexity"]),
                    "supplier_id": material["supplier_id"],
                },
            )
        conn.commit()


def insert_suppliers(suppliers_df, engine):
    """
    Insert suppliers into the database.

    Args:
        suppliers_df (pd.DataFrame): Suppliers data
        engine: SQLAlchemy engine
    """
    with engine.connect() as conn:
        for _, supplier in suppliers_df.iterrows():
            # Insert supplier
            conn.execute(
                text(
                    """
                INSERT INTO suppliers (
                    supplier_id, name, location, delivery_time_days,
                    reliability_score, price_level, contact
                ) VALUES (
                    :supplier_id, :name, :location, :delivery_time_days,
                    :reliability_score, :price_level, :contact
                )
                ON CONFLICT (supplier_id) DO NOTHING
                """
                ),
                {
                    "supplier_id": supplier["supplier_id"],
                    "name": supplier["name"],
                    "location": supplier["location"],
                    "delivery_time_days": int(supplier["delivery_time_days"]),
                    "reliability_score": int(supplier["reliability_score"]),
                    "price_level": supplier["price_level"],
                    "contact": supplier["contact"],
                },
            )
        conn.commit()


if __name__ == "__main__":
    init_database()
