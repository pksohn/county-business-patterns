from __future__ import division
import pandas as pd
from pandas import DataFrame


def location_quotient(df, totals, value_col='EMP', naics_col='NAICS2012', geog_col='county'):
    """
    Calculates location quotient for each row in a DataFrame of smaller geographies (e.g. counties) when compared to
    a DataFrame of the same indicator (job or establishment counts) in a larger geography (e.g. state).

    Parameters
    ----------
    df : DataFrame
        DataFrame where each row includes a count of jobs or establishments for one NAICS industry in one geography.
    totals : DataFrame
        DataFrame where each row is the larger geography total in a NAICS industry. DataFrame must be indexed by NAICS
        code and must include the same value_col. The Counties.total() method provides this format.
    value_col : str, optional
        Name of column with the count of interest (jobs or establishments)
    naics_col : str, optional
        Name of column with the NAICS code in small_df
    geog_col : str, optional
        Name of column with the geography (e.g. county) in small_df

    Returns
    -------

    """

    if not isinstance(df, DataFrame):
        raise TypeError('small_df must be DataFrame')

    if value_col not in df.columns:
        raise ValueError('Name passed to value_col not found in small_df column names')

    if naics_col not in df.columns:
        raise ValueError('Name passed to naics_col not found in small_df column names')

    if geog_col not in df.columns:
        raise ValueError('Name passed to geog_col not found in small_df column names')

    if not isinstance(totals, DataFrame):
        raise TypeError('large_df must be DataFrame')

    df = pd.DataFrame(data=df)
    df['location_quotient'] = None

    for index, row in df.iterrows():

        geo = row[geog_col]
        naics = row[naics_col]

        # Numerator
        E_industry_small = row[value_col]
        total_emp_row = df[(df[geog_col] == geo) & (df[naics_col] == '00')]
        E_total_small = total_emp_row[value_col].iloc[0]

        numerator = E_industry_small / E_total_small

        # Denominator
        E_industry_large = totals.loc[naics, value_col]
        E_total_large = totals.loc['00', value_col]

        denominator = E_industry_large / E_total_large

        # Location Quotient
        df.loc[index, 'location_quotient'] = numerator / denominator

    return df