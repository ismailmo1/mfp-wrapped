import asyncio
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from myfitnesspal.diary_scraping import (
    async_get_diary_data,
    async_scrape_diaries,
)

load_dotenv()


async def async_load_mfp_data(start_date: date, end_date: date, user: str):

    extracted_diaries = await async_scrape_diaries(start_date, end_date, user)
    prog_bar = st.progress(0)
    date_update = st.empty()
    diary_df = pd.DataFrame()
    progress = 0
    num_days = (end_date - start_date).days + 1

    for idx, df in enumerate(async_get_diary_data(extracted_diaries)):
        progress = round((idx + 1) / num_days, 2)
        prog_bar.progress(progress)
        date_update.text(
            f"grabbing diary for {start_date + timedelta(days=idx)}"
        )

        diary_df = pd.concat([diary_df, df], axis=0, join="outer")

    date_update.empty()

    return diary_df


@st.cache(suppress_st_warning=True)
def grab_mfp_data(start_date, end_date, user):
    return asyncio.run(async_load_mfp_data(start_date, end_date, user))


def show_metrics(metrics: dict) -> None:
    """show all metrics on one row

    Args:
        metrics (dict): dict of form: label = key, value= (value, delta)
    """
    num_columns = len(metrics)
    columns = st.columns(num_columns)
    for idx, (key, item) in enumerate(metrics.items()):

        if isinstance(item, tuple):
            columns[idx].metric(label=key, value=item[0], delta=item[1])
        else:
            columns[idx].metric(label=key, value=item)
