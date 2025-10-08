import streamlit as st

def highlight_uea(row):
    return ['background-color: gold; color: black; font-weight: bold'] * len(row) \
        if row['institution'] == "The University of East Anglia" else [''] * len(row)


def load_custom_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
