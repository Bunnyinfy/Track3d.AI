"""
Machine learning model module for the construction material recommendation system.

"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestRegressor
from material_data import generate_material_database, get_material_properties
from data_utils import preprocess_material_data, extract_project_features


class MaterialRecommender:
    """Material recommendation model class."""

    def __init__(self):
        """Initialize the material recommender model."""
        self.materials_df = generate_material_database()
        self.features_df = preprocess_material_data(self.materials_df)
        self.scaler = StandardScaler()
        self.scaled_features = self.scaler.fit_transform(self.features_df)
        self.knn_model = NearestNeighbors(n_neighbors=5, algorithm="auto")
        self.knn_model.fit(self.scaled_features)
        self.rf_model = None
        self.trained = False

    def get_materials_df(self):
        """
        Get the materials dataframe.

        Returns:
            pd.DataFrame: Materials database
        """
        return self.materials_df

    def train_regression_model(self, project_specs_list, ratings_list):
        """
        Train a random forest regression model based on user ratings.

        Args:
            project_specs_list (list): List of project specifications
            ratings_list (list): List of user ratings for materials

        Returns:
            bool: True if training was successful
        """
        if len(project_specs_list) < 5 or len(ratings_list) < 5:
            return False

        # Extract features from project specifications
        project_features_list = []
        for specs in project_specs_list:
            project_features = extract_project_features(specs)
            project_features_list.append(project_features)

        # Combine project features
        X = pd.concat(project_features_list, ignore_index=True)

        # Use ratings as target variable
        y = np.array(ratings_list)

        # Train a random forest regressor
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.rf_model.fit(X, y)
        self.trained = True

        return True

    def get_similar_materials(self, material_id, n_neighbors=3):
        """
        Get similar materials based on the material ID.

        Args:
            material_id (int): Material ID
            n_neighbors (int): Number of similar materials to return

        Returns:
            list: List of similar material IDs
        """

        # Get the index of the material in the dataframe
        material_idx = self.materials_df[self.materials_df["id"] == material_id].index[
            0
        ]

        # Get the feature vector for the material
        material_features = self.scaled_features[material_idx].reshape(1, -1)

        # Find the nearest neighbors
        distances, indices = self.knn_model.kneighbors(
            material_features, n_neighbors=n_neighbors + 1
        )

        # Skip the first neighbor as it's the material itself
        similar_indices = indices[0][1:]
        similar_materials = self.materials_df.iloc[similar_indices]

        return similar_materials["id"].tolist()

    def predict_material_ratings(self, project_specs):
        """
        Predict material ratings based on project specifications.

        Args:
            project_specs (dict): Project specifications

        Returns:
            pd.DataFrame: Materials with predicted ratings
        """
        if not self.trained or self.rf_model is None:
            return None

        # Extract features from project specifications
        project_features = extract_project_features(project_specs)

        # Predict ratings for all materials
        predicted_ratings = self.rf_model.predict(project_features)

        # Create a dataframe with materials and their predicted ratings
        rated_materials = self.materials_df.copy()
        rated_materials["predicted_rating"] = predicted_ratings

        # Sort by predicted rating in descending order
        rated_materials = rated_materials.sort_values(
            by="predicted_rating", ascending=False
        )

        return rated_materials

    def recommend_materials(self, project_specs, n_recommendations=5):
        """
        Recommend materials based on project specifications.

        Args:
            project_specs (dict): Project specifications
            n_recommendations (int): Number of recommendations to return

        Returns:
            pd.DataFrame: Recommended materials
        """
        from data_utils import calculate_material_scores

        # Calculate scores for each material based on project specifications
        scored_materials = calculate_material_scores(self.materials_df, project_specs)

        # Return the top N recommendations
        return scored_materials.head(n_recommendations)
