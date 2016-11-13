from __future__ import division
import pandas as pd
import os


def update_naics(years, old_series):
    """
    Updates NAICS codes from 2002 to 2007 scheme, or from 2007 to 2012.

    Parameters
    ----------
    years : str
        Must be one of '2002-2007' or '2007-2012'
    old_series : Pandas Series
        Series of old NAICS codes to be updated

    Returns
    -------
    Pandas Series of new NAICS codes
    """

    reference_file = {
        '2002-2007': os.path.join(os.path.dirname(__file__), '2002_to_2007_NAICS.csv'),
        '2007-2012': os.path.join(os.path.dirname(__file__), '2012_to_2007_NAICS.csv')
    }

    reference_old_column = {
        '2002-2007': 'naics2002',
        '2007-2012': 'naics2007'
    }

    reference_new_column = {
        '2002-2007': 'naics2007',
        '2007-2012': 'naics2012'
    }

    old_col = reference_old_column[years]
    new_col = reference_new_column[years]

    reference = pd.read_csv(reference_file[years], dtype=str, index_col=old_col)
    ref_dict = reference.to_dict()[new_col]
    translation = pd.DataFrame(old_series)

    def translate_naics(row):
        old_naics = row.iloc[0]

        if old_naics in ref_dict.keys():
            new_naics = ref_dict[old_naics]
        else:
            new_naics = old_naics

        return new_naics

    translation['new_naics'] = translation.apply(translate_naics, axis=1)

    return translation['new_naics']


def location_quotient(small, large):
    """
    Calculates location quotient given two Pandas Series with equivalent industry identifiers.

    Parameters
    ----------
    small : Series
        Series of smaller geography
    large : Series
        Series of larger geography

    Returns
    -------
    Pandas Series
    """

    if not all(isinstance(i, pd.Series) for i in [small, large]):
        raise TypeError('small and large must be Series')

    if not all(i in large.index for i in small.index):
        raise ValueError('large index must include all values of small index')

    df = pd.DataFrame(data=small)
    df.columns = ['small']
    df['large'] = large

    for index, row in df.iterrows():
        # Numerator
        E_industry_small = row.small
        total_emp_row = df.loc['00']
        E_total_small = total_emp_row.small

        numerator = E_industry_small / E_total_small

        # Denominator
        E_industry_large = row.large
        E_total_large = total_emp_row.large

        denominator = E_industry_large / E_total_large

        # Location Quotient
        df.loc[index, 'location_quotient'] = numerator / denominator

    return df.location_quotient


def shift_share(small_old, small_new, large_old, large_new):
    """
    Calculates shift share given

    Parameters
    ----------
    small_old
    small_new
    large_old
    large_new

    Returns
    -------

    """

    if not all(isinstance(i, pd.Series) for i in [small_old, small_new, large_old, large_new]):
        raise TypeError('All arguments must be Series')

    if not all(large_new.index == large_old.index):
        raise ValueError('large series indices must be equal')

    if not all(small_new.index == small_old.index):
        raise ValueError('small series indices must be equal')

    if not all(i in large_new.index for i in small_new.index):
        raise ValueError('large index must include all values of small index')

    df = pd.DataFrame(small_old)
    df.columns = 'small_old'
    df['small_new'] = small_new
    df['large_old'] = large_old
    df['large_new'] = large_new

    # Large Growth Share
    large_growth_rate = (df.large_new['00'] - df.large_old['00']) / df.large_old['00']
    df['large_growth_share'] = df['small_old'] * large_new

    # Industry Mix
    df['large_industry_growth_rate'] = (df.large_new - df.large_old) / df.large_old

    df['industry_mix'] = df.apply(lambda row: row['small_old'] *
                                              (row['large_industry_growth_rate'] - large_growth_rate),
                                  axis=1)

    # Local Competitiveness
    df['small_industry_growth_rate'] = (df.small_new - df.small_old) / df.small_old
    df['local_competitiveness'] = df.apply(lambda row: row['small_old'] *
                                                       (row['small_industry_growth_rate'] -
                                                        row['large_industry_growth_rate']),
                                           axis=1)

    return df