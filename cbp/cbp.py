import pandas as pd
from pandas import DataFrame
import requests
import sys


class Counties(DataFrame):
    """
    DataFrame of County Business Patterns data for all counties in a given state.

    Parameters
    ----------
    state_fips : str
        Two-digit FIPS code for the state
    year : str, optional
        Year of data to download (if downloading data). Default is 2015.
    read_from : str, optional
        Must be one of 'api' and 'csv'. Default is 'api'.
    key : str, optional
        API key from the Census Bureau
    variables : list, optional
        List of variables (as str) to download, default list is provided
    filepath : str, optional
        File path to csv file if that option is desired
    """

    def __init__(self, state_fips, year=2014, read_from='api', key=None, variables=None, filepath=None):

        dtypes = {
            'NAICS2012': str,
            'county': str,
            'state': str
        }

        if read_from == 'api':

            if not key:
                raise ValueError('If reading from Census API, must provide API key in the key parameter')

            baseurl = 'http://api.census.gov/data/{}/cbp'.format(year)

            if variables:
                cbp_vars = ','.join(variables)
            else:
                cbp_vars = 'EMP,ESTAB,NAICS2012,NAICS2012_TTL,GEO_TTL'

            url = '{baseurl}?get={cbp_vars}&for=county:*&in=state:{state_fips}&key={key}'.format(**locals())

            try:
                req = requests.get(url)
                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print err
                sys.exit(1)

            results = pd.read_json(req.text, orient='index', dtype=dtypes).T
            results.columns = results.iloc[0]
            results.drop(results.index[0], inplace=True)

            data = results

        elif read_from == 'csv':

            if not filepath:
                raise ValueError('If reading from CSV file, must provide path to file in filepath parameter')

            data = pd.read_csv(filepath_or_buffer=filepath, dtype=dtypes)

        else:
            raise ValueError('Valid options for the read_from parameter are "api" and "csv".')

        DataFrame.__init__(self, data=data)

    def county(self, county):
        """
        Returns a subset of the Counties DataFrame for one or more specified counties.

        Parameters
        ----------
        county : str or list
            County FIPS code or list of FIPS codes

        Returns
        -------
        DataFrame

        """

        if isinstance(county, list):
            result = self[self.county in county]
        elif isinstance(county, str):
            result = self[self.county == county]
        else:
            raise TypeError('County identifier must be str')
        return result

    def two_digit(self, county=None):
        """
        Returns a reduced version of the Counties DataFrame with only 2-digit NAICS codes, filtered by county if
        optional parameter is passed.

        Parameters
        ----------
        county : str or list, optional
            County FIPS code or list of FIPS codes

        Returns
        -------

        """
        two_digits = self[(self.NAICS2012.str.len() == 2) |
                          (self.NAICS2012.str.contains('-'))]

        if county:
            if isinstance(county, list):
                result = two_digits[two_digits.county.isin(county)]
            elif isinstance(county, str):
                result = two_digits[two_digits.county == county]
            else:
                raise TypeError('County identifier must be str')
            return result

        else:
            return two_digits

    def three_digit(self, county=None):
        """
        Returns a reduced version of the Counties DataFrame with only 3-digit NAICS codes, filtered by county if
        optional parameter is passed.

        Parameters
        ----------
        county : str or list, optional
            County FIPS code or list of FIPS codes

        Returns
        -------

        """
        three_digits = self[(self.NAICS2012.str.len() == 3) | (self.NAICS2012 == '00')]

        if county:
            if isinstance(county, list):
                result = three_digits[three_digits.county.isin(county)]
            elif isinstance(county, str):
                result = three_digits[three_digits.county == county]
            else:
                raise TypeError('County identifier must be str')
            return result

        else:
            return three_digits

    def total(self):
        """
        Returns a DataFrame with totals of employment and establishments for each NAICS2012 code in the Counties object.

        Returns
        -------
        DataFrame

        """
        grouped = self.groupby(by='NAICS2012')

        agg_by = {
            'EMP': 'sum',
            'ESTAB': 'sum'
        }

        return grouped.agg(agg_by)
