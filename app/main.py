import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Solar Challenge Dashboard")

# --- Load Data Function ---
# This function will load the cleaned data for all countries
@st.cache_data # Cache the data loading for better performance
def load_data():
    countries = ['benin', 'sierra_leone', 'togo']
    all_dfs = []
    
    # Get the directory of the current script (main.py)
    # This ensures the path is robust regardless of where the Streamlit app is run from
    script_dir = os.path.dirname(__file__)
    
    for country in countries:
        # Construct the path to the cleaned CSV.
        # From script_dir (e.g., '.../solar-challenge-week1/app'),
        # go up one level ('..') to the project root ('.../solar-challenge-week1'),
        # then into the 'data' directory, then the specific country_clean.csv
        file_path = os.path.join(script_dir, '..', 'data', f'{country}_clean.csv')
        
        # --- DEBUGGING LINE (remove or comment out once confirmed working) ---
        st.write(f"Attempting to load: `{file_path}`") 
        # -------------------------------------------------------------------
        
        try:
            df = pd.read_csv(file_path, parse_dates=['Timestamp'])
            df['country'] = country.replace('_', ' ').title() # Capitalize for display
            all_dfs.append(df)
        except FileNotFoundError:
            st.error(f"Error: Cleaned data for {country.replace('_', ' ').title()} not found at `{file_path}`. "
                     "Please ensure Task 2 is completed and CSVs are in the 'data/' folder.")
            return None # Indicate failure to load data if any file is missing

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        return combined_df
    return None # Return None if no dataframes were successfully loaded

df_all = load_data()

# --- Dashboard Title ---
st.title("☀️ Solar Potential Across West Africa")
st.markdown("An interactive dashboard to explore solar irradiance and environmental factors in Benin, Sierra Leone, and Togo.")

if df_all is not None: # Only proceed if data was successfully loaded
    # --- Sidebar for Country Selection ---
    st.sidebar.header("Filter Options")
    
    # Get unique country names from the loaded data
    available_countries = df_all['country'].unique().tolist()
    
    # Widget to select countries
    selected_countries = st.sidebar.multiselect(
        "Select Countries for Comparison:",
        options=available_countries,
        default=available_countries # Default to all countries selected
    )

    # Filter data based on selection
    df_filtered = df_all[df_all['country'].isin(selected_countries)]

    # --- Main Content Area ---

    # 1. Boxplot of GHI distribution by country
    st.header("Global Horizontal Irradiance (GHI) Distribution")
    if not df_filtered.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='country', y='GHI', data=df_filtered, palette='viridis', ax=ax)
        ax.set_title('GHI Distribution by Country')
        ax.set_xlabel('Country')
        ax.set_ylabel('GHI (W/m²)')
        st.pyplot(fig)
    else:
        st.info("Please select at least one country to view the GHI distribution.")

    # 2. Summary Statistics for Selected Countries
    st.header("Summary Statistics for Selected Countries")
    if not df_filtered.empty:
        summary_metrics = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'BP', 'WS', 'WSgust']
        # Filter to only include metrics that exist in the DataFrame
        existing_summary_metrics = [m for m in summary_metrics if m in df_filtered.columns]
        
        if existing_summary_metrics:
            summary_table = df_filtered.groupby('country')[existing_summary_metrics].agg(['mean', 'median', 'std'])
            st.dataframe(summary_table.style.format("{:.2f}")) # Format to 2 decimal places
        else:
            st.info("No relevant metrics found for summary statistics.")
    else:
        st.info("No data available for the selected countries to generate summary statistics.")

    # 3. Daily Average GHI over Time (simple line chart)
    st.header("Daily Average GHI Over Time")
    if not df_filtered.empty:
        # Resample to daily average
        df_daily_avg_ghi = df_filtered.set_index('Timestamp').groupby('country')['GHI'].resample('D').mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='Timestamp', y='GHI', hue='country', data=df_daily_avg_ghi, ax=ax)
        ax.set_title('Daily Average GHI')
        ax.set_xlabel('Date')
        ax.set_ylabel('Average GHI (W/m²)')
        ax.legend(title='Country')
        plt.xticks(rotation=45) # Rotate x-axis labels for better readability
        st.pyplot(fig)
    else:
        st.info("No data to display daily GHI averages for selected countries.")

    # You can add more interactive elements and plots here, for example:
    # Hourly Average Irradiance
    st.header("Hourly Average Irradiance")
    if not df_filtered.empty:
        df_filtered['Hour'] = df_filtered['Timestamp'].dt.hour
        hourly_avg = df_filtered.groupby(['country', 'Hour'])[['GHI', 'DNI', 'DHI']].mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='Hour', y='GHI', hue='country', data=hourly_avg, ax=ax, marker='o', label='GHI')
        sns.lineplot(x='Hour', y='DNI', hue='country', data=hourly_avg, ax=ax, marker='x', linestyle='--', label='DNI')
        sns.lineplot(x='Hour', y='DHI', hue='country', data=hourly_avg, ax=ax, marker='^', linestyle=':', label='DHI')
        ax.set_title('Average Irradiance by Hour of Day')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Irradiance (W/m²)')
        ax.set_xticks(range(0, 24))
        st.pyplot(fig)
    else:
        st.info("No data to display hourly average irradiance for selected countries.")

else:
    # This block is executed if load_data() returned None
    st.error("Dashboard cannot function because essential data could not be loaded. "
             "Please ensure Task 2 is completed, cleaned CSV files exist, and the paths are correct.")