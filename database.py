"""
Database module for the Construction Material Recommendation System.
This module contains the database models and setup.
"""

import os
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class Material(db.Model):
    """Material model representing construction materials in the database."""
    
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    applications = db.Column(db.JSON, nullable=False)  # Stored as JSON array
    strength_mpa = db.Column(db.Float, nullable=False)
    durability_years = db.Column(db.Integer, nullable=False)
    thermal_conductivity = db.Column(db.Float, nullable=False)
    fire_resistance_hours = db.Column(db.Float, nullable=False)
    water_resistance = db.Column(db.Integer, nullable=False)
    eco_friendly_score = db.Column(db.Integer, nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Integer, nullable=False)
    maintenance_requirement = db.Column(db.Integer, nullable=False)
    weather_resistance = db.Column(db.JSON, nullable=False)  # Stored as JSON object
    installation_complexity = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.String(20), db.ForeignKey('suppliers.supplier_id'), nullable=False)
    
    # Define relationship with supplier
    supplier = db.relationship('Supplier', backref=db.backref('materials', lazy=True))
    
    def __repr__(self):
        return f'<Material {self.name}>'
    
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'applications': self.applications,
            'strength_mpa': self.strength_mpa,
            'durability_years': self.durability_years,
            'thermal_conductivity': self.thermal_conductivity,
            'fire_resistance_hours': self.fire_resistance_hours,
            'water_resistance': self.water_resistance,
            'eco_friendly_score': self.eco_friendly_score,
            'cost_per_unit': self.cost_per_unit,
            'availability': self.availability,
            'maintenance_requirement': self.maintenance_requirement,
            'weather_resistance': self.weather_resistance,
            'installation_complexity': self.installation_complexity,
            'supplier_id': self.supplier_id
        }

class Supplier(db.Model):
    """Supplier model representing material suppliers in the database."""
    
    __tablename__ = 'suppliers'
    
    supplier_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    delivery_time_days = db.Column(db.Integer, nullable=False)
    reliability_score = db.Column(db.Integer, nullable=False)
    price_level = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
    
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'supplier_id': self.supplier_id,
            'name': self.name,
            'location': self.location,
            'delivery_time_days': self.delivery_time_days,
            'reliability_score': self.reliability_score,
            'price_level': self.price_level,
            'contact': self.contact
        }

class Project(db.Model):
    """Project model for storing user project specifications."""
    
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    applications = db.Column(db.JSON, nullable=False)  # Stored as JSON array
    material_types = db.Column(db.JSON, nullable=True)  # Stored as JSON array
    min_strength_mpa = db.Column(db.Float, default=0)
    min_durability_years = db.Column(db.Integer, default=0)
    fire_resistance_requirement = db.Column(db.Float, default=0)
    water_resistance_requirement = db.Column(db.Integer, default=0)
    thermal_requirement = db.Column(db.String(20), nullable=True)
    eco_friendly_requirement = db.Column(db.Integer, default=0)
    budget_constraint = db.Column(db.Float, nullable=True)
    installation_time_constraint = db.Column(db.String(20), nullable=True)
    environmental_conditions = db.Column(db.JSON, nullable=True)  # Stored as JSON object
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship with recommendations
    recommendations = db.relationship('Recommendation', back_populates='project', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'applications': self.applications,
            'material_types': self.material_types,
            'min_strength_mpa': self.min_strength_mpa,
            'min_durability_years': self.min_durability_years,
            'fire_resistance_requirement': self.fire_resistance_requirement,
            'water_resistance_requirement': self.water_resistance_requirement,
            'thermal_requirement': self.thermal_requirement,
            'eco_friendly_requirement': self.eco_friendly_requirement,
            'budget_constraint': self.budget_constraint,
            'installation_time_constraint': self.installation_time_constraint,
            'environmental_conditions': self.environmental_conditions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Recommendation(db.Model):
    """Recommendation model for storing material recommendations for projects."""
    
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationships
    project = db.relationship('Project', back_populates='recommendations')
    material = db.relationship('Material')
    
    def __repr__(self):
        return f'<Recommendation {self.id}>'
    
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'material_id': self.material_id,
            'score': self.score,
            'rank': self.rank,
            'created_at': self.created_at.isoformat(),
            'material': self.material.serialize if self.material else None
        }

class UserFeedback(db.Model):
    """User feedback model for storing user ratings and comments on materials."""
    
    __tablename__ = 'user_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 star rating
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship with material
    material = db.relationship('Material')
    
    def __repr__(self):
        return f'<UserFeedback {self.id}>'
    
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'material_id': self.material_id,
            'project_id': self.project_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

def init_db(app):
    """Initialize the database with the Flask app."""
    # Check if DATABASE_URL exists
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Fix for Postgres URLs starting with postgres:// instead of postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

def seed_database(app, materials_df, suppliers_df):
    """
    Seed the database with initial material and supplier data.
    
    Args:
        app: Flask application
        materials_df: Pandas DataFrame containing material data
        suppliers_df: Pandas DataFrame containing supplier data
    """
    with app.app_context():
        # Check if suppliers already exist
        if Supplier.query.count() == 0:
            # Add suppliers
            for _, supplier_data in suppliers_df.iterrows():
                supplier = Supplier(
                    supplier_id=supplier_data['supplier_id'],
                    name=supplier_data['name'],
                    location=supplier_data['location'],
                    delivery_time_days=supplier_data['delivery_time_days'],
                    reliability_score=supplier_data['reliability_score'],
                    price_level=supplier_data['price_level'],
                    contact=supplier_data['contact']
                )
                db.session.add(supplier)
            
            db.session.commit()
            print("Suppliers added to database")
        
        # Check if materials already exist
        if Material.query.count() == 0:
            # Add materials
            for _, material_data in materials_df.iterrows():
                material = Material(
                    id=material_data['id'],
                    name=material_data['name'],
                    type=material_data['type'],
                    applications=material_data['applications'],
                    strength_mpa=material_data['strength_mpa'],
                    durability_years=material_data['durability_years'],
                    thermal_conductivity=material_data['thermal_conductivity'],
                    fire_resistance_hours=material_data['fire_resistance_hours'],
                    water_resistance=material_data['water_resistance'],
                    eco_friendly_score=material_data['eco_friendly_score'],
                    cost_per_unit=material_data['cost_per_unit'],
                    availability=material_data['availability'],
                    maintenance_requirement=material_data['maintenance_requirement'],
                    weather_resistance=material_data['weather_resistance'],
                    installation_complexity=material_data['installation_complexity'],
                    supplier_id=material_data['supplier_id']
                )
                db.session.add(material)
            
            db.session.commit()
            print("Materials added to database")