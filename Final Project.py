"""
Name: Masego Seleka
CS230: Section 5
Data: NY-House-Dataset
URL:
Description: This Streamlit app is an interactive dashboard that analyzes housing data for New York City using a CSV dataset. It provides a user-friendly interface with six tabs, each answering a key question about the NYC real estate market.
"""
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk

path = "C:/Users/Maseg/OneDrive - Bentley University/Bentley Documents/Spring 2025/CS230/CS230 pythonProject/Final Project/"

# [DA1], [PY1] Load and clean data
def read_data(filepath='NY-House-Dataset.csv'):
    df = pd.read_csv(path + filepath)
    df = df[(df['PRICE'] > 0) & (df['PROPERTYSQFT'] > 0)]
    return df


# [PY2] Function that returns more than one value
def summarize_extremes(df):
    max_row = df[df['PRICE'] == df['PRICE'].max()].iloc[0]
    min_row = df[df['PRICE'] == df['PRICE'].min()].iloc[0]
    return max_row['SUBLOCALITY'], min_row['SUBLOCALITY']


# [PY3] Try/except for cost calc
def cost_per_sqft_by_sublocality():
    try:
        df = read_data()
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return {}
    cost_dict = {}
    for sub in df['SUBLOCALITY'].unique():
        sub_df = df[df['SUBLOCALITY'] == sub]
        total_price = sub_df['PRICE'].sum()
        total_sqft = sub_df['PROPERTYSQFT'].sum()
        if total_sqft > 0:
            cost_dict[sub] = round(total_price / total_sqft, 2)
    return cost_dict


# [DA9], [PY4] List comprehension for averages
def avg_sqft_by_sublocality():
    df = read_data()
    return {
        sub: round(df[df['SUBLOCALITY'] == sub]['PROPERTYSQFT'].mean(), 2)
        for sub in df['SUBLOCALITY'].unique()
    }


# [PY5] Dictionary use
def plot_bar_chart(data_dict, title, xlabel, ylabel, rotation=45):
    keys = list(data_dict.keys())
    values = list(data_dict.values())
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(keys, values)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='x', rotation=rotation)
    st.pyplot(fig)


def plot_pie_chart_streamlit(data_dict, title, figsize=(6, 6)):
    labels = list(data_dict.keys())
    sizes = list(data_dict.values())
    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title(title)
    ax.axis('equal')
    st.pyplot(fig)



st.set_page_config(page_title="NYC Housing Insights", layout="wide")
st.sidebar.title("Filter Settings")

df = read_data()

# [DA2] Sorting options
price_options = sorted(set(p for p in df['PRICE'].unique() if p % 50000 == 0))
min_price = st.sidebar.selectbox("Select Min Price", price_options, index=price_options.index(500000))  # [ST2]
max_price = st.sidebar.selectbox("Select Max Price", price_options, index=price_options.index(1000000))

# [ST3] Slider for zoom
zoom_level = st.sidebar.slider("Map Zoom Level", 0.0, 15.0, 10.0)

# [ST2] Bedrooms
bedroom_options = sorted(df['BEDS'].unique())
bed_slider = st.sidebar.selectbox("Select Min Bedrooms", bedroom_options, index=bedroom_options.index(3))

st.title("NYC Housing Data Explorer")

# [ST4] Tab layout
tabs = st.tabs([
    "Most Expensive House",
    "Avg Cost per SqFt",
    "Filtered Homes Map",
    "Avg SqFt by Sublocality",
    "Bedroom Distribution",
    "Filterable Table"
])

# [DA3], [MAP]
with tabs[0]:
    st.subheader("Most Expensive House Location")
    expensive_home = df[df['PRICE'] == df['PRICE'].max()]
    view_state_q1 = pdk.ViewState(
        latitude=expensive_home["LATITUDE"].values[0],
        longitude=expensive_home["LONGITUDE"].values[0],
        zoom=13, pitch=0
    )
    layer_q1 = pdk.Layer("ScatterplotLayer", data=expensive_home,
                         get_position='[LONGITUDE, LATITUDE]', get_radius=200,
                         get_color=[255, 0, 0], pickable=True)
    tooltip_q1 = {
        "html": "<b>Address:</b> {FORMATTED_ADDRESS}<br/><b>Price:</b> ${PRICE}<br/><b>Beds:</b> {BEDS}<br/><b>SqFt:</b> {PROPERTYSQFT}",
        "style": {"backgroundColor": "black", "color": "white"}
    }
    st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/streets-v12',
                             initial_view_state=view_state_q1, layers=[layer_q1], tooltip=tooltip_q1))

    max_sub, min_sub = summarize_extremes(df)  # [PY2]
    st.write(f"Most expensive sublocality: **{max_sub}**")
    st.write(f"Least expensive sublocality: **{min_sub}**")

# [VIZ1]
with tabs[1]:
    st.subheader("Average Cost per SqFt by Sublocality")
    cost_dict = cost_per_sqft_by_sublocality()
    plot_bar_chart(cost_dict, "Avg Cost per SqFt", "Sublocality", "$/SqFt", rotation=90)

# [DA4, DA5], [MAP]
with tabs[2]:
    st.subheader("Map of Homes Within Selected Price & Bedroom Range")
    filtered = df[(df['PRICE'] >= min_price) & (df['PRICE'] <= max_price) & (df['BEDS'] >= bed_slider)]
    if filtered.empty:
        st.warning("No listings match the selected price and bedroom filters. Please try different values.")
    else:
        view_state = pdk.ViewState(
            latitude=filtered["LATITUDE"].mean(),
            longitude=filtered["LONGITUDE"].mean(),
            zoom=zoom_level
        )
        layer = pdk.Layer(
            'ScatterplotLayer', data=filtered,
            get_position='[LONGITUDE, LATITUDE]',
            get_radius=150, get_color=[200, 30, 0, 160], pickable=True
        )
        tooltip = {
            "html": "<b>Address:</b> {FORMATTED_ADDRESS}<br/><b>Price:</b> ${PRICE}<br/><b>Beds:</b> {BEDS}",
            "style": {"backgroundColor": "black", "color": "white"}
        }
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v12',
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ))

# [VIZ2]
with tabs[3]:
    st.subheader("Average Square Footage by Sublocality")
    avg_sqft_dict = avg_sqft_by_sublocality()
    plot_bar_chart(avg_sqft_dict, "Avg Square Footage", "Sublocality", "SqFt", rotation=90)

# [VIZ3]
with tabs[4]:
    st.subheader("Bedroom Count Distribution")
    bedroom_counts = df['BEDS'].value_counts().sort_index()
    bedroom_counts_grouped = {}
    for beds, count in bedroom_counts.items():
        label = f"{int(beds)} BR" if beds <= 6 else "7+ BR"
        bedroom_counts_grouped[label] = bedroom_counts_grouped.get(label, 0) + count
    plot_pie_chart_streamlit(bedroom_counts_grouped, "Bedroom Distribution")

# [DA2], [DA4], [DA5], [VIZ3] Table
with tabs[5]:
    st.subheader("Filterable and Sortable Table of Listings")

    important_columns = ['SUBLOCALITY', 'PRICE', 'BEDS', 'BATH', 'PROPERTYSQFT', 'FORMATTED_ADDRESS']
    table_df = df[important_columns]

    selected_sublocality = st.selectbox("Filter by sublocality", options=["All"] + sorted(df['SUBLOCALITY'].unique()))
    max_price_input = st.number_input("Maximum price", value=int(table_df['PRICE'].max()))

    if selected_sublocality != "All":
        table_df = table_df[table_df['SUBLOCALITY'] == selected_sublocality]
    table_df = table_df[table_df['PRICE'] <= max_price_input]

    sort_column = st.selectbox("Sort by", options=important_columns, index=1)
    sort_order = st.radio("Sort order", ["Ascending", "Descending"])
    ascending = sort_order == "Ascending"

    sorted_df = table_df.sort_values(by=sort_column, ascending=ascending)
    st.dataframe(sorted_df.reset_index(drop=True), use_container_width=True)
