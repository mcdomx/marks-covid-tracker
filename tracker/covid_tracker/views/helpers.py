import os
import logging
import pandas as pd
import geopandas as gpd

# for census data used in Bubble maps
from census import Census

# import variables in the local .env file
from dotenv import load_dotenv

load_dotenv(verbose=False)

# avoid chained assignment warnings
pd.options.mode.chained_assignment = None

# GLOBAL VARIABLES
FILE_PATH = os.path.join('COVID-19', 'csse_covid_19_data', 'csse_covid_19_time_series')

territories = ['American Samoa', 'Guam', 'Northern Mariana Islands', 'Mariana Islands',
               'Puerto Rico', 'Virgin Islands', 'Diamond Princess', 'Grand Princess']

political_affiliations = {'American Samoa': 'na',
                          'Guam': 'na',
                          'Northern Mariana Islands': 'na',
                          'Puerto Rico': 'na',
                          'Virgin Islands': 'na',
                          'Alabama': 'red',
                          'Alaska': 'red',
                          'Arizona': 'red',
                          'Arkansas': 'red',
                          'California': 'blue',
                          'Colorado': 'purple',
                          'Connecticut': 'blue',
                          'Delaware': 'blue',
                          'District of Columbia': 'blue',
                          'Florida': 'red',
                          'Georgia': 'red',
                          'Hawaii': 'blue',
                          'Idaho': 'red',
                          'Illinois': 'blue',
                          'Indiana': 'purple',
                          'Iowa': 'red',
                          'Kansas': 'red',
                          'Kentucky': 'red',
                          'Louisiana': 'red',
                          'Maine': 'blue',
                          'Maryland': 'blue',
                          'Massachusetts': 'blue',
                          'Michigan': 'blue',
                          'Minnesota': 'blue',
                          'Mississippi': 'red',
                          'Missouri': 'red',
                          'Montana': 'red',
                          'Nebraska': 'red',
                          'Nevada': 'purple',
                          'New Hampshire': 'purple',
                          'New Jersey': 'blue',
                          'New Mexico': 'purple',
                          'New York': 'blue',
                          'North Carolina': 'purple',
                          'North Dakota': 'red',
                          'Ohio': 'purple',
                          'Oklahoma': 'red',
                          'Oregon': 'blue',
                          'Pennsylvania': 'blue',
                          'Rhode Island': 'blue',
                          'South Carolina': 'red',
                          'South Dakota': 'red',
                          'Tennessee': 'red',
                          'Texas': 'red',
                          'Utah': 'red',
                          'Vermont': 'blue',
                          'Virginia': 'purple',
                          'Washington': 'blue',
                          'West Virginia': 'red',
                          'Wisconsin': 'blue',
                          'Wyoming': 'red',
                          'Diamond Princess': 'na',
                          'Grand Princess': 'na'}


# GET CSV DATA, CLEAN DATA, AND PLACE INTO DICTIONARY FOR EASY ACCESS
def get_dataframe(dataset, file_path: str = FILE_PATH) -> pd.DataFrame:
    file_names = {
        'recovered_global': 'time_series_covid19_recovered_global.csv',
        'deaths_global': 'time_series_covid19_deaths_global.csv',
        'deaths_US': 'time_series_covid19_deaths_US.csv',
        'confirmed_global': 'time_series_covid19_confirmed_global.csv',
        'confirmed_US': 'time_series_covid19_confirmed_US.csv'
    }

    file_name = file_names.get(dataset)

    def get_pol_aff(s):
        return political_affiliations.get(s.Province_State, 'na')

    def make_county_state(s):
        return f"{s.County}, {s.Province_State}"

    f = os.path.join(file_path, file_name)

    if os.path.isfile(f):
        df = pd.read_csv(f)
        if "Province_State" in df.columns:
            # add political affiliation
            df['political_affiliation'] = df.apply(get_pol_aff, axis=1)

            if "Admin2" in df.columns:
                df = df.rename(columns={'Admin2': 'County'})
                df['County_State'] = df.apply(make_county_state, axis=1)

            # format FIPS
            df['FIPS'] = df['UID'].astype(str).apply(lambda x: x[3:])

            # add population by county
            c = Census(os.getenv("CENSUS_API_KEY"), year=2010)
            county_population = pd.DataFrame(
                c.sf1.state_county(['NAME', 'P001001'], state_fips=Census.ALL, county_fips=Census.ALL))
            county_population.rename(
                columns={'P001001': 'population', 'state': 'state_fips', 'county': 'county_fips'}, inplace=True)
            county_population.population = county_population.population.astype(int)
            county_population['FIPS'] = county_population.state_fips + county_population.county_fips
            df = df.merge(county_population[['FIPS', 'population']], on=['FIPS'])

    else:
        if not os.path.isdir(file_path):
            logging.error(f"NOT A PATH: '{file_path}''")
        else:
            logging.error(f"NOT A FILE: '{file_name}''")

    # delete jan and feb
    cols_to_remove = []
    for c in df.columns:
        spl = c.split('/')
        if len(spl) == 3 and spl[2] == '20':
            if spl[0] == '1' or spl[0] == '2':
                cols_to_remove.append(c)
    df.drop(columns=cols_to_remove, inplace=True)

    # remove territories
    if "Province_State" in df.columns:
        df = df[~df.Province_State.isin(territories)]

    # convert to GeoPandas if there are lat and lon coordinates
    if "Lat" in df.columns and "Long_" in df.columns:
        df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Long_, df.Lat))

    return df


# OTHER GLOBAL VARIABLES
ATTR_COLS = ['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'County', 'Province_State', 'County_State', 'Country_Region',
             'Lat', 'Long_', 'Combined_Key', 'political_affiliation', 'geometry', 'population']
DATE_COLS_TEXT = [c for c in get_dataframe('confirmed_US').columns if c not in ATTR_COLS]
DATE_COLS_DATES = pd.to_datetime(DATE_COLS_TEXT)


# SUPPORT FUNCTIONS
# group by state
def get_df_by_state(_df) -> pd.DataFrame:
    return _df.groupby(by='Province_State').sum().reset_index()


# group by county in a state
def get_df_by_counties(_df, state) -> pd.DataFrame:
    return _df[_df.Province_State == state]


def get_rankings(_df, top_n=None) -> list:
    A_COLS = [c for c in _df.columns if c in ATTR_COLS]

    rv_df = _df[DATE_COLS_TEXT].rank(ascending=False)
    rv_df = pd.concat([_df.loc[rv_df.index][A_COLS], rv_df], axis=1)

    if top_n is not None:
        return rv_df.nsmallest(top_n, DATE_COLS_TEXT[-1]).sort_values(by=DATE_COLS_TEXT[-1], ascending=True)

    return rv_df.sort_values(by=DATE_COLS_TEXT[-1])


# get data per day
def get_by_day(_df):
    daily = _df[DATE_COLS_TEXT] - _df[DATE_COLS_TEXT].shift(axis=1)
    attr_cols = set(_df.columns) - set(DATE_COLS_TEXT)
    daily = pd.concat([_df[attr_cols], daily], axis=1)

    return daily


def get_daily_growth_rate(_df):
    _df = get_by_day(_df)
    daily_rate = _df[DATE_COLS_TEXT] / _df[DATE_COLS_TEXT].shift(axis=1)
    attr_cols = set(_df.columns) - set(DATE_COLS_TEXT)
    daily_rate = pd.concat([_df[attr_cols], daily_rate], axis=1)
    daily_rate = daily_rate.fillna(1)
    return daily_rate
