import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# -------------------------------
# Page configuration
st.set_page_config(
    page_title="My Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# Inject Custom CSS
st.markdown(
    """
    <style>
    /* Main page background */
    .stApp {
        background-color: #f0f2f6;
    }

    /* Title style */
    h1 {
        color: #4B8BBE;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }

    /* Sidebar background */
    .css-1d391kg {
        background-color: #e6f2ff;
    }

    /* Metric boxes style */
    .stMetric {
        font-size: 18px;
        color: #333333;
    }

    /* Table header styling */
    .stDataFrame thead th {
        background-color: #4B8BBE;
        color: white;
    }

    /* Streamlit buttons styling */
    div.stButton > button:first-child {
        background-color: #4B8BBE;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Page title
st.title("📊 My Streamlit Dashboard")

# -------------------------------
# Upload datasets
st.sidebar.header("Upload CSV Files")
file1 = st.sidebar.file_uploader("Upload first CSV file", type=["csv"])
file2 = st.sidebar.file_uploader("Upload second CSV file", type=["csv"])

if file1 and file2:
    # Read CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Optionally merge datasets or choose which one to use
    # For demo, let's just use the first dataset for charts
    df = df1.copy()

    # Sidebar filters
    if "Category" in df.columns:
        selected_category = st.sidebar.selectbox(
            "Select Category:",
            df["Category"].unique()
        )
        filtered_df = df[df["Category"] == selected_category]
    else:
        filtered_df = df

    # -------------------------------
    # Display KPIs using columns
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", len(filtered_df))
    if "Value" in filtered_df.columns:
        col2.metric("Total Value", filtered_df["Value"].sum())
    if "Sales" in filtered_df.columns:
        col3.metric("Average Sales", f"${filtered_df['Sales'].mean():,.0f}")

    # -------------------------------
    # Display chart
    st.subheader("Bar Chart")
    if "Category" in filtered_df.columns and "Value" in filtered_df.columns:
        fig = px.bar(filtered_df, x="Category", y="Value", color="Category", text="Value")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Display table
    st.subheader("Data Table")
    st.dataframe(filtered_df)

else:
    st.warning("Please upload **both CSV files** to view the dashboard.")
