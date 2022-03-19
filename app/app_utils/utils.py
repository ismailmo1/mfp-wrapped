import os
from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from myfitnesspal.diary_scraping import get_diary_data

load_dotenv()


@st.cache(suppress_st_warning=True)
def load_mfp_data(start_date: date, end_date: date):
    prog_bar = st.progress(0)
    diary_df = pd.DataFrame()
    progress = 0
    num_days = (end_date - start_date).days

    for df in get_diary_data(
        start_date,
        end_date,
        public=False,
        user=os.environ["MFP_USER"],
        pwd=os.environ["MFP_PASS"],
    ):
        progress += 1 / num_days
        prog_bar.progress(round(progress, 2))

        diary_df = pd.concat([diary_df, df], axis=0, join="outer")

    return diary_df
