import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import plotly.express as px
from copyright import display_custom_license
import numpy as np
import plotly.express as px
import time
from sidebar_content import sidebar_content

st.set_page_config(layout = "wide", 
                    page_title='Geographic Bias Tool',
                    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtoX76TyVQs-o1vEvNuAnYX0zahtSui173gg&s",
                    initial_sidebar_state="auto") 
pd.set_option('display.max_colwidth', None)

# home_page = st.Page('Home.py', title='Affiliation finder')
# reference_finder = st.Page('Reference_finder.py', title='Reference finder')
# reference_finder2 = st.Page('Reference_finder copy.py', title='Reference finder2')

# pg = st.navigation([home_page, reference_finder, reference_finder2])

# pg.run()

sidebar_content() 

st.markdown(
    """
    <a href="https://www.imperial.ac.uk">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Imperial_College_London_new_logo.png" width="300">
    </a>
    """,
    unsafe_allow_html=True
)
st.title('Geographic Bias Tool', anchor=False)

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

st.subheader('Welcome!')
st.write('''
    Welcome to the Geographic Bias Tool! 
''')

st.link_button('Publication affiliation finder','https://test-gbt.streamlit.app/Affiliation_finder')
st.page_link('tools/Affiliation_finder.py', label='Publication affiliation finder')
st.page_link('tools/Reference_finder.py', label='Reference affiliation finder')

st.divider()

display_custom_license()