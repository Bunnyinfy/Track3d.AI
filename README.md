
# 🧱 BuildWise – AI-Powered Construction Material Recommendation System

BuildWise is a Streamlit-based intelligent recommendation platform designed to assist construction professionals in selecting the most suitable building materials for their projects. By integrating machine learning with a clean, interactive interface, BuildWise enables data-driven decisions that balance performance, cost, sustainability, and environmental compatibility.

---

## 🚀 Features

### ✅ Project Specification Form
- Input your project details: application type, material preferences, strength, durability, budget, fire/water resistance, and more.
- Specify environmental conditions (heat, cold, humidity, UV exposure).

### ✅ Smart Material Recommendations
- Recommends top materials using a hybrid ML model:
  - **K-Nearest Neighbors** for material similarity
  - **Random Forest Regressor** for personalized scoring

### ✅ Material Comparison
- Add multiple materials to a comparison list.
- Visualize trade-offs across:
  - Durability
  - Cost
  - Environmental and weather resistance
  - Supplier reliability

### ✅ Cost Analysis
- Estimate total cost based on project size.
- Compare material options in a cost-efficient manner.
- View detailed breakdowns and interactive charts.

### ✅ Supplier Insights
- Get key supplier details: location, delivery time, reliability, and pricing.
- Visualize supplier comparisons.

### ✅ User Authentication & Project Management
- Secure login/logout functionality.
- Save and retrieve previous project configurations.

### ✅ Help & Support
- Built-in documentation, definitions, and contact information.

---

## 🛠️ Tech Stack

- **Frontend & Backend**: [Streamlit](https://streamlit.io/)
- **ML Models**: `scikit-learn` (KNN, Random Forest)
- **Visualization**: `plotly`, `streamlit-option-menu`
- **Data Handling**: `pandas`, `numpy`
- **Authentication & State**: Streamlit session state + custom logic
- **DataBase**: PostgreSQL

---

## 🌍 Use Cases

- **Architects** selecting facade or insulation materials
- **Contractors** evaluating trade-offs between cost and durability
- **Green building consultants** prioritizing eco-friendly materials
- **Procurement teams** comparing supplier reliability
- **Real estate developers** managing multiple project specs and material decisions

---


## ✉️ Contact

For queries or support:
- Email: penugondasrinivas20@gmail.com

---

**Build smart. Build sustainable. BuildWise.**
