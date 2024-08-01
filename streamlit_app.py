import streamlit as st

home_page = st.Page('Home.py', title='Affiliation finder')
reference_finder = st.Page('Reference_finder.py', title='Reference finder')
reference_finder2 = st.Page('Reference_finder copy.py', title='Reference finder2')

pg = st.navigation([home_page, reference_finder, reference_finder2])
st.set_page_config(page_title="Affiliationfinder", page_icon=":material/edit:")

pg.run()