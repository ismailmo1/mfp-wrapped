import time
from datetime import date

import pandas as pd
import streamlit as st

st.title("Seven years of Ismail trying not be fat")

prog_bar = st.progress(0)


@st.cache
def load_mfp_data(start_date: date, end_date: date):
    df = pd.read_csv("myfitnesspal/mfp-extract-2021.csv", index_col=0)
    return df


for i in range(0, 101):
    prog_bar.progress(i)
    time.sleep(0.01)


st.write(load_mfp_data(date(2021, 1, 1), date(2021, 12, 31)))
