st.markdown(
    """
    <style>
    /* General background & text */
    body, .stApp {
        background-color: #202225;  /* soft-dark */
        color: #f0f0f0;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stSubheader, .stTitle {
        color: #ffffff !important;
    }

    /* Dataframes and tables */
    .stDataFrame, .stTable {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
        border-radius: 6px;
    }
    table {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
    }
    th {
        background-color: #23272a !important;
        color: #ffffff !important;
    }
    td {
        color: #e4e6eb !important;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stMultiSelect div, .stDateInput input {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
        border-radius: 4px;
        border: 1px solid #444;
    }

    /* Buttons */
    button, .stButton>button {
        background-color: #5865f2 !important; /* UEA-friendly purple/blue accent */
        color: white !important;
        border-radius: 6px;
        border: none;
    }
    button:hover, .stButton>button:hover {
        background-color: #4752c4 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)