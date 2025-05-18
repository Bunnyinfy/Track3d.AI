"""
Database utility functions for the construction material recommendation system.
This module handles database connections and operations.
"""

import streamlit as st
import os
import json
from sqlalchemy import (
    create_engine,
    text,
    Column,
    Integer,
    String,
    Float,
    JSON,
    ForeignKey,
    DateTime,
    TIMESTAMP,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from passlib.hash import pbkdf2_sha256
import pandas as pd

# Create a SQLAlchemy engine

DATABASE_URL = st.secrets["DATABASE_URL"]
print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(DATABASE_URL)


# Create a Base class for declarative models
Base = declarative_base()


# Define models
class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    projects = relationship(
        "UserProject", back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def hash_password(cls, password):
        """Hash a password for storing."""
        return pbkdf2_sha256.hash(password)

    @classmethod
    def verify_password(cls, stored_hash, provided_password):
        """Verify a stored password against a provided password."""
        return pbkdf2_sha256.verify(provided_password, stored_hash)


class UserProject(Base):
    """User projects model for storing saved projects."""

    __tablename__ = "user_projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    project_name = Column(String(100), nullable=False)
    project_specs = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    user = relationship("User", back_populates="projects")


# Create a Session class
Session = sessionmaker(bind=engine)


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)


def get_material_from_db():
    """
    Get materials from the database.

    Returns:
        pd.DataFrame: DataFrame containing material information
    """
    with Session() as session:
        result = session.execute(text("SELECT * FROM materials"))
        materials = []

        for row in result:
            material = {
                "id": row.id,
                "name": row.name,
                "type": row.type,
                "applications": (
                    json.loads(row.applications)
                    if isinstance(row.applications, str)
                    else row.applications
                ),
                "strength_mpa": row.strength_mpa,
                "durability_years": row.durability_years,
                "thermal_conductivity": row.thermal_conductivity,
                "fire_resistance_hours": row.fire_resistance_hours,
                "water_resistance": row.water_resistance,
                "eco_friendly_score": row.eco_friendly_score,
                "cost_per_unit": row.cost_per_unit,
                "availability": row.availability,
                "maintenance_requirement": row.maintenance_requirement,
                "weather_resistance": (
                    json.loads(row.weather_resistance)
                    if isinstance(row.weather_resistance, str)
                    else row.weather_resistance
                ),
                "installation_complexity": row.installation_complexity,
                "supplier_id": row.supplier_id,
            }
            materials.append(material)

        return pd.DataFrame(materials)


def get_supplier_from_db():
    """
    Get suppliers from the database.

    Returns:
        pd.DataFrame: DataFrame containing supplier information
    """
    with Session() as session:
        result = session.execute(text("SELECT * FROM suppliers"))
        suppliers = []

        for row in result:
            supplier = {
                "supplier_id": row.supplier_id,
                "name": row.name,
                "location": row.location,
                "delivery_time_days": row.delivery_time_days,
                "reliability_score": row.reliability_score,
                "price_level": row.price_level,
                "contact": row.contact,
            }
            suppliers.append(supplier)

        return pd.DataFrame(suppliers)


def register_user(username, email, password):
    """
    Register a new user.

    Args:
        username (str): Username
        email (str): Email address
        password (str): Password

    Returns:
        bool: True if registration was successful, False otherwise
    """
    try:
        with Session() as session:
            # Check if username or email already exists
            existing_user = (
                session.query(User)
                .filter((User.username == username) | (User.email == email))
                .first()
            )

            if existing_user:
                return False

            # Hash password
            password_hash = User.hash_password(password)

            # Create new user
            new_user = User(username=username, email=email, password_hash=password_hash)

            session.add(new_user)
            session.commit()

            return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False


def authenticate_user(username_or_email, password):
    """
    Authenticate a user.

    Args:
        username_or_email (str): Username or email
        password (str): Password

    Returns:
        User: User object if authentication was successful, None otherwise
    """
    try:
        with Session() as session:
            # Find user by username or email
            user = (
                session.query(User)
                .filter(
                    (User.username == username_or_email)
                    | (User.email == username_or_email)
                )
                .first()
            )

            if user and User.verify_password(user.password_hash, password):
                return user

            return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None


def save_user_project(user_id, project_name, project_specs):
    """
    Save a user project.

    Args:
        user_id (int): User ID
        project_name (str): Project name
        project_specs (dict): Project specifications

    Returns:
        int: Project ID if successful, None otherwise
    """
    try:
        with Session() as session:
            # Create new project
            new_project = UserProject(
                user_id=user_id, project_name=project_name, project_specs=project_specs
            )

            session.add(new_project)
            session.commit()

            return new_project.id
    except Exception as e:
        print(f"Error saving project: {e}")
        return None


def get_user_projects(user_id):
    """
    Get projects for a user.

    Args:
        user_id (int): User ID

    Returns:
        list: List of projects
    """
    try:
        with Session() as session:
            projects = (
                session.query(UserProject)
                .filter(UserProject.user_id == user_id)
                .order_by(UserProject.updated_at.desc())
                .all()
            )

            project_list = []
            for project in projects:
                project_dict = {
                    "id": project.id,
                    "name": project.project_name,
                    "specs": project.project_specs,
                    "created_at": project.created_at,
                    "updated_at": project.updated_at,
                }
                project_list.append(project_dict)

            return project_list
    except Exception as e:
        print(f"Error getting user projects: {e}")
        return []


def delete_user_project(project_id, user_id):
    """
    Delete a user project.

    Args:
        project_id (int): Project ID
        user_id (int): User ID to ensure only the owner can delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        with Session() as session:
            # Find project
            project = (
                session.query(UserProject)
                .filter(UserProject.id == project_id, UserProject.user_id == user_id)
                .first()
            )

            if not project:
                return False

            # Delete project
            session.delete(project)
            session.commit()

            return True
    except Exception as e:
        print(f"Error deleting project: {e}")
        return False


def get_project_by_id(project_id, user_id):
    """
    Get a project by ID.

    Args:
        project_id (int): Project ID
        user_id (int): User ID to ensure only the owner can access

    Returns:
        dict: Project if found, None otherwise
    """
    try:
        with Session() as session:
            project = (
                session.query(UserProject)
                .filter(UserProject.id == project_id, UserProject.user_id == user_id)
                .first()
            )

            if not project:
                return None

            return {
                "id": project.id,
                "name": project.project_name,
                "specs": project.project_specs,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
            }
    except Exception as e:
        print(f"Error getting project: {e}")
        return None


def update_user_project(project_id, user_id, project_name, project_specs):
    """
    Update a user project.

    Args:
        project_id (int): Project ID
        user_id (int): User ID to ensure only the owner can update
        project_name (str): Project name
        project_specs (dict): Project specifications

    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        with Session() as session:
            # Find project
            project = (
                session.query(UserProject)
                .filter(UserProject.id == project_id, UserProject.user_id == user_id)
                .first()
            )

            if not project:
                return False

            # Update project
            project.project_name = project_name
            project.project_specs = project_specs
            # Set updated_at timestamp in the database
            session.execute(
                text(
                    "UPDATE user_projects SET updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                ),
                {"id": project_id},
            )

            session.commit()

            return True
    except Exception as e:
        print(f"Error updating project: {e}")
        return False


def check_and_create_tables():
    """Check if tables exist and create them if they don't."""
    create_tables()
