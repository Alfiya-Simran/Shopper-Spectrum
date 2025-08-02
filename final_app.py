import streamlit as st
import numpy as np
import pandas as pd
import pickle
import gdown
import os

# Ensure gdown is installed (only on first-time execution)
try:
    import gdown
except ImportError:
    os.system("pip install gdown")

# Download product_similarity.pkl if not present
if not os.path.exists("product_similarity.pkl"):
    file_id = "1jGXWvbhCXwfuhn9D-q2x7f1EvzLKt0Op"
    gdown.download(f"https://drive.google.com/uc?id={file_id}", "product_similarity.pkl", quiet=False)

# Load models and data
with open("rfm_clustering_model.pkl", "rb") as f:
    clustering_model = pickle.load(f)
with open("rfm_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("product_similarity.pkl", "rb") as f:
    product_similarity = pickle.load(f)

# Prepare product list
products = list(product_similarity.keys())

# Prediction logic
def predict_segment(recency, frequency, monetary):
    features = np.array([[recency, frequency, monetary]])
    scaled = scaler.transform(features)
    cluster = clustering_model.predict(scaled)[0]
    cluster_labels = {0: "High-Value", 1: "Regular", 2: "Occasional", 3: "At-Risk"}
    return cluster, cluster_labels.get(cluster, "Unknown")

# Recommendation logic
def recommend_products(product_name):
    if product_name not in product_similarity:
        return ["No similar products found."]
    similar_items = sorted(product_similarity[product_name].items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in similar_items[1:6]]  # Top 5 excluding input product

# Streamlit UI
st.set_page_config(page_title="Shopper Spectrum", layout="wide")
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to", ["Home", "Clustering", "Recommendation"])

if app_mode == "Home":
    st.title("🛒 Shopper Spectrum")
    st.markdown("""
    **Features:**
    - **Customer Segmentation:** Predicts customer segment based on Recency, Frequency, and Monetary values.
    - **Product Recommendation:** Suggests top 5 similar products for a given product.
    """)

elif app_mode == "Clustering":
    st.title("Customer Segmentation")
    recency = st.number_input("Recency (days since last purchase)", min_value=0, value=30)
    frequency = st.number_input("Frequency (number of purchases)", min_value=0, value=5)
    monetary = st.number_input("Monetary (total spend)", min_value=0.0, value=1000.0)

    if st.button("Predict Segment"):
        cluster, segment_label = predict_segment(recency, frequency, monetary)
        st.success(f"**Cluster {cluster} → {segment_label} Shopper**")

elif app_mode == "Recommendation":
    st.title("Product Recommender")
    product_name = st.text_input("Enter Product Name", "")
    if st.button("Recommend"):
        if product_name:
            recommended = recommend_products(product_name.upper())
            st.subheader("Recommended Products:")
            for prod in recommended:
                st.write(f"- {prod}")
        else:
            st.warning("Please enter a product name.")
