import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import pandas as pd
import plotly.express as px

# Load data set
file_path = "C:/Users/hp/Documents/map app/grid3_nga_-_health_facilities_-1.csv"
data = pd.read_csv(file_path)

# Filter data for Kano state and select specific columns
data = data[(data['statename'] == 'Kano')][['prmry_name', 'hospital_type', 'func_stats', 'LGA', 'latitude', 'longitude', 'wardname', 'globalid', 'ownership']]

# Group hospitals by type and LGA
hospital_counts = data.groupby(['LGA', 'hospital_type']).size().reset_index(name='count')

# Sidebar for navigation
tabs = ['Interactive Map', 'Data Cleaning Process', 'README']
selected_tab = st.sidebar.selectbox("Select Tab", tabs)

# Add Logo and Heading at the Top
st.image("logo.png", width=200)  # Add your logo image here
st.title("Kano Interactive Map with Indicators")

# Define color mapping for hospital types
color_mapping = {
    'Comprehensive Health Center': 'blue',
    'Cottage Hospital': 'green',
    'Dispensary': 'orange',
    'Educational Clinic': 'purple',
    'Federal Medical Center': 'red',
    'Federal Staff Clinic': 'pink',
    'General Hospital': 'lightblue',
    'Laboratory': 'yellow',
    'Maternity Home': 'lightgreen',
    'Medical Center': 'brown',
    'Military and Paramilitary Clinic': 'darkred',
    'Primary Health Center': 'cyan',
    'Private Non Profit': 'magenta',
    'Specialist Hospital': 'gold',
    'Teaching Hospital': 'gray'
}

# Sidebar Features (Reordered)

# 1. Theme Toggle
theme = st.sidebar.radio("Choose Theme", ['Light', 'Dark'], index=0)
if theme == 'Dark':
    st.markdown("<style>body { background-color: black; color: white; }</style>", unsafe_allow_html=True)

# 2. Search Hospital by Name
search_term = st.sidebar.text_input("Search Hospital by Name")
if search_term:
    data = data[data['prmry_name'].str.contains(search_term, case=False)]

# 3. Multi-select for LGAs
unique_lgas = data['LGA'].unique()
selected_lgas = st.sidebar.multiselect("Select Multiple LGAs", options=unique_lgas, default=unique_lgas)

# Filter data based on selected LGAs
filtered_data = data[data['LGA'].isin(selected_lgas)]

# 4. Image-based filter for Hospital Types
st.sidebar.markdown("### Filter by Hospital Type")
selected_types = st.sidebar.multiselect("Select Hospital Types", options=list(color_mapping.keys()), default=list(color_mapping.keys()))
filtered_data = filtered_data[filtered_data['hospital_type'].isin(selected_types)]

# 5. Download Filtered Data as CSV
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_data)
st.sidebar.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')

# Tab 1: Interactive Map
if selected_tab == 'Interactive Map':
    st.header("Explore Hospitals by Local Government Area (LGA)")

    # Create a base map focused on Kano State
    map_center = [12.0, 8.5]
    
    # Create the map with default tile layer
    m = folium.Map(location=map_center, zoom_start=10, tiles='OpenStreetMap', attr='Map data © OpenStreetMap contributors')

    # Create a marker cluster
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for hospitals
    for i, row in filtered_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=(f"{row['prmry_name']} - Type: {row['hospital_type']} - LGA: {row['LGA']}"),
            tooltip=(f"{row['prmry_name']}<br>Type: {row['hospital_type']}<br>LGA: {row['LGA']}"),
            icon=folium.Icon(color=color_mapping.get(row['hospital_type'], 'gray'))  # Default color if type not found
        ).add_to(marker_cluster)

    # Display the map
    st_folium(m, width=800, height=600)

    # Show total hospitals and filtered LGA
    total_hospitals = filtered_data.shape[0]
    col1, col2 = st.columns(2)
    col1.metric("Total Selected Hospitals", total_hospitals)

    # Pie Chart for Hospital Types
    hospital_counts_filtered = hospital_counts[hospital_counts['LGA'].isin(selected_lgas)] if selected_lgas else hospital_counts
    total_count = hospital_counts_filtered['count'].sum()
    hospital_counts_filtered['percentage'] = (hospital_counts_filtered['count'] / total_count) * 100

    fig_pie = px.pie(hospital_counts_filtered, names='hospital_type', values='percentage', 
                     title='Percentage of Hospitals by Type',
                     hover_data=['count'],
                     color='hospital_type',
                     color_discrete_map=color_mapping,  # Match pie chart colors to map pin colors
                     template='plotly_white')

    # Display the pie chart
    st.plotly_chart(fig_pie, use_container_width=True)

# Tab 2: README
elif selected_tab == 'README':
    st.title("README")
    st.markdown(""" 
    ## Interactive Map Web App built with Python
    This web app displays an interactive map with various indicators for medical centres in Kano.
    You can filter hospitals by Local Government Area (LGA) and view their types.
    
    ### Features
    - Filters by the left side to select `Local Governments` or/and `Hospital Types`
    - Search bar to find hospitals by name
    - Interactive map with tooltips and popup details for each hospital.
    - Marker clustering to group nearby hospitals i.e when you zoom out near by hospital will cluster and indicate a count number, you can clik on the cluster to zoom in.
    - Pie chart to visualize hospital types by percentage.
    - You can download the filtered raw data
    
    The data was extracted from a public data repository `https://data.humdata.org/`
    This app is developed by `Ady_Techy` using `Streamlit`, `Folium`, `Pandas`, and `Plotly`.
    """)

# Tab 3: Data Cleaning Process
elif selected_tab == 'Data Cleaning Process':
    st.title("Data Cleaning Process")
    
    st.write("### Original Data")
    st.dataframe(data)

    st.markdown("### Cleaning Steps:")
    st.markdown("""1. **Latitude and Longitude Rounding**: The latitude and longitude values were rounded to four decimal places to reduce unnecessary precision and the necessary columns were extracted.
    2. **No additional cleaning applied in this example**.
    """)

    # Optionally, show cleaned data
    cleaned_data = data.copy()  
    st.write("### Cleaned Data")
    st.dataframe(cleaned_data)
