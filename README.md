# Note: I'm writing a new, much improved version of this called "cbpy"
In progress [here](https://github.com/pksohn/cbpy).

# County Business Patterns wrapper and economic analysis tools

This repository includes tools for downloading and working with County Business Patterns economic data from the US Census Bureau.
You will need an API key from the [Census Bureau](http://www.census.gov/developers/) to download data.

Dependencies: pandas, requests

## Downloading CBP data

Example of downloading data for Texas (default year is 2014, the latest year of data offered as of November 2016): 

```
from cbp import Counties
texas = Counties(state_fips='48', read_from='api', key='CENSUS_KEY_HERE')
texas.head()
``` 

| EMP   | ESTAB | NAICS2012 | NAICS2012_TTL         | GEO_TTL         | state | county |
|-------|-------|-----------|-----------------------|-----------------|-------|--------|
| 11738 | 940   | 0         | Total for all sectors | Anderson County | 48    | 1      |
| 5683  | 403   | 0         | Total for all sectors | Andrews County  | 48    | 3      |
| 30525 | 1857  | 0         | Total for all sectors | Angelina County | 48    | 5      |
| 4131  | 503   | 0         | Total for all sectors | Aransas County  | 48    | 7      |
| 1539  | 201   | 0         | Total for all sectors | Archer County   | 48    | 9      |


Use the `two_digit` method to look at two-digit NAICS industry codes for a simplified view.
You can also pass county FIPS codes to the `county` parameter to filter for a specific county.
Let's look at Travis County, the largest county in the Austin area.

```
travis = texas.two_digit(county='453')
travis.head()
```

| EMP    | ESTAB | NAICS2012 | NAICS2012_TTL                                 | GEO_TTL       | state | county |
|--------|-------|-----------|-----------------------------------------------|---------------|-------|--------|
| 544038 | 32217 | 0         | Total for all sectors                         | Travis County | 48    | 453    |
| 21     | 9     | 11        | Agriculture, Forestry, Fishing and Hunting    | Travis County | 48    | 453    |
| 851    | 131   | 21        | Mining, Quarrying, and Oil and Gas Extraction | Travis County | 48    | 453    |
| 1046   | 66    | 22        | Utilities                                     | Travis County | 48    | 453    |
| 30343  | 2097  | 23        | Construction                                  | Travis County | 48    | 453    |

## Analyzing CBP data

You can pass two Pandas Series with NAICS codes as indices, one for Travis County, one for Texas, to calculate a location quotient:

```
from cbp import utils

# Create series for employment by sector for Texas
texas_emp = texas.two_digit().groupby('NAICS2012').agg('sum').EMP
# Create series for employment by sector for Travis County
travis_emp = travis.set_index('NAICS2012').EMP

# Use utils.location_quotient to calculate LQ
lq = utils.location_quotient(travis_emp, texas_emp)
print lq
``` 

| NAICS | Location Quotient|
|-------|----------------|
| 00    | 1.000000       |
| 11    | 0.094953       |
| 21    | 0.076681       |
| 22    | 0.513275       |
| 23    | 0.920357       |
| 31-33 | 0.643649       |

If you have data for two years (2006 and 2014 in this case), you can pass similar Series to the above for both years to calculate shift share:

```
# Get 2006 data for change-over-time analysis
texas06 = Counties(state_fips='48', year=2006, read_from='csv', filepath='texas_cbp_2006.csv')
travis_06 = texas06.two_digit(county='453')

# Get 2006 series for Travis County and Texas employment by sector
travis_emp_06 = travis_06.set_index('NAICS2012').EMP
texas_emp_06 = texas06.two_digit().groupby('NAICS2012').agg('sum').EMP

# Pass the 4 series (2014 and 2006 employment for Texas and for Travis County) to shift share function
shift_share, shift_share_summary = utils.shift_share(small_old=travis_emp_06,
                                                     small_new=travis_emp,
                                                     large_old=texas_emp_06,
                                                     large_new=texas_emp)

print shift_share_summary
```


|                       | description                                       | absolute     | percentage |
|-----------------------|---------------------------------------------------|--------------|------------|
| small_growth          | Growth in smaller geography                       | 82367        | 0.178435   |
| large_growth          | Growth in larger geography                        | 784017       | 0.090705   |
| large_growth_share    | Growth attributable to larger geography growth rate | 47013.015779 | 0.570775   |
| industry_mix          | Growth attributable to industry mix               | -7067.789264 | -0.085809  |
| local_competitiveness | Growth attributable to local competitiveness      | 42421.773485 | 0.515034   |
