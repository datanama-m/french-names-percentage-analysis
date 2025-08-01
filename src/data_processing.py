import pandas as pd
from functools import lru_cache

GENDER_MAP = {1: 'Male', 2: 'Female'}


def load_and_preprocess_data(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename, delimiter=';')
    df.columns = ['Gender', 'Name', 'Year', 'Count']
    df = df[df['Name'] != '_PRENOMS_RARES']
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').dropna().astype(int)
    df['Name'] = df['Name'].str.upper()
    df['Gender'] = df['Gender'].map(GENDER_MAP)
    return df


def calculate_percentages(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentage of births for each name."""
    df_agg = df.groupby(['Name', 'Year', 'Gender'], as_index=False)['Count'].sum()

    total_counts = (
        df.groupby(['Year', 'Gender'], as_index=False)['Count']
        .sum()
        .rename(columns={'Count': 'Total_Count'})
    )

    merged_df = pd.merge(df_agg, total_counts, on=['Year', 'Gender'])

    merged_df['Percentage'] = (merged_df['Count'] / merged_df['Total_Count']) * 100

    return merged_df.sort_values(['Name', 'Gender', 'Year'])


@lru_cache(maxsize=1)
def get_processed_data(filename: str) -> pd.DataFrame:
    raw_df = load_and_preprocess_data(filename)
    return calculate_percentages(raw_df)
