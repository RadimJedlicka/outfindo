import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ######################## ###################################################
# STREAMLIT PAGE STRUCTURE 
# ######################## ###################################################

st.set_page_config(
    page_title="Map of bike eshops", 
    page_icon=":bike:", 
    layout="wide", 
    initial_sidebar_state="auto",
)

st.markdown('''<h1 style='text-align: center;'>
                Map of bike e-shops in France and Italy</h1>
                ''', 
                unsafe_allow_html=True
)


df = pd.read_csv('dealers.csv')

# Plot map of active and inactive stations
fig = px.scatter_mapbox(
    df,
    lat='lat', 
    lon='lng', 
    zoom=4, 
    width=1800, 
    height=800,
    # title='Active and inactive stations',
    color='country',
    hover_name= 'eshop',
    color_discrete_sequence=['green', 'red'],
    mapbox_style='stamen-terrain'
)

st.plotly_chart(fig, use_container_width=True, sharing="streamlit")