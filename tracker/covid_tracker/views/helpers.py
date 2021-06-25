import os
import logging
import pandas as pd
import geopandas as gpd
import datetime

# for census data used in Bubble maps
from census import Census

# import variables in the local .env file
from dotenv import load_dotenv

load_dotenv(verbose=False)

# avoid chained assignment warnings
pd.options.mode.chained_assignment = None

# GLOBAL VARIABLES
FILE_PATH = os.path.join('covid_tracker', 'COVID-19', 'csse_covid_19_data', 'csse_covid_19_time_series')

territories = ['American Samoa', 'Guam', 'Northern Mariana Islands', 'Mariana Islands',
               'Puerto Rico', 'Virgin Islands', 'Diamond Princess', 'Grand Princess']

# affiliation of governor in 2019
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
                          'Colorado': 'blue',
                          'Connecticut': 'blue',
                          'Delaware': 'blue',
                          'District of Columbia': 'blue',
                          'Florida': 'red',
                          'Georgia': 'red',
                          'Hawaii': 'blue',
                          'Idaho': 'red',
                          'Illinois': 'blue',
                          'Indiana': 'red',
                          'Iowa': 'red',
                          'Kansas': 'blue',
                          'Kentucky': 'blue',
                          'Louisiana': 'blue',
                          'Maine': 'blue',
                          'Maryland': 'red',
                          'Massachusetts': 'red',
                          'Michigan': 'blue',
                          'Minnesota': 'blue',
                          'Mississippi': 'red',
                          'Missouri': 'red',
                          'Montana': 'blue',
                          'Nebraska': 'red',
                          'Nevada': 'blue',
                          'New Hampshire': 'red',
                          'New Jersey': 'blue',
                          'New Mexico': 'blue',
                          'New York': 'blue',
                          'North Carolina': 'blue',
                          'North Dakota': 'red',
                          'Ohio': 'red',
                          'Oklahoma': 'red',
                          'Oregon': 'blue',
                          'Pennsylvania': 'blue',
                          'Rhode Island': 'blue',
                          'South Carolina': 'red',
                          'South Dakota': 'red',
                          'Tennessee': 'red',
                          'Texas': 'red',
                          'Utah': 'red',
                          'Vermont': 'red',
                          'Virginia': 'blue',
                          'Washington': 'blue',
                          'West Virginia': 'red',
                          'Wisconsin': 'blue',
                          'Wyoming': 'red',
                          'Diamond Princess': 'na',
                          'Grand Princess': 'na'}


# GET CSV DATA, CLEAN DATA, AND PLACE INTO DICTIONARY FOR EASY ACCESS
def get_dataframe(dataset, file_path: str = FILE_PATH) -> dict:
    """
    Support function that will retrieve a dictionary which includes a dataset in a dataframe format for simplified downstream sorting and filtering.

    :param dataset: The string name of the dataset for which data is retrieved ('recovered_global', 'deaths_global', 'deaths_US', 'confirmed_global', 'confirmed_US')
    :param file_path: (optional) The root filepath where the applicable data is stored.

    :return: Returns a dictionary with the dataframe along with applicable parameters useful in handling the dataset. The dictionary container the following key-values {'df': <dataframe>, 'attr_cols': <list of names of attribute columns>, 'date_cols_text': <list of date columns in text format>, 'date_cols_dates': <list of date columns in datetime format>}
    """
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
    if not os.path.isfile(f):
        logging.error(f"{f} is not a file.")

    df = pd.DataFrame()
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

    # remove US territories
    if "Province_State" in df.columns:
        df = df[~df.Province_State.isin(territories)]

    # convert to GeoPandas if there are lat and lon coordinates
    if "Lat" in df.columns and "Long_" in df.columns:
        df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Long_, df.Lat))

    attr_cols, date_cols_text, date_cols_dates = get_column_groups(df)

    return {'df': df, 'attr_cols': attr_cols, 'date_cols_text': date_cols_text, 'date_cols_dates': date_cols_dates}


def get_column_groups(df):
    """
    Returns a tuple of 3 lists that include the columns of a dataframe split into 3 groups. 'Attribute Columns' are non-date columns in a dataframe,  'Date Columns Text' are date columns in text format and 'Date Columns Date' are date columns in datetime format.

    :param df:  The dataframe that will be evaluated and for which the column groups are returned.

    :return: A tuple of 3 lists: the attribute columns (all columns that are not dates), date columns in text format and the date columns is datetime format.
    """
    date_cols_dates = pd.to_datetime(df.columns, errors='coerce')
    date_cols_tf = [not pd.isnull(c) for c in date_cols_dates]
    date_cols_dates = date_cols_dates[date_cols_tf]
    date_cols_text = df.columns[date_cols_tf]
    attr_cols = df.columns[[not c for c in date_cols_tf]]

    return attr_cols, date_cols_text, date_cols_dates


# SUPPORT FUNCTIONS
# group by state
def get_df_by_state(_df) -> pd.DataFrame:
    """
    Support function that will return a dataframe grouped by 'Province State' where values are summed.

    :param _df:  The dataframe that will be grouped.

    :return: The grouped dataframe
    """
    return _df.groupby(by='Province_State').sum().reset_index()


# group by county in a state
def get_df_by_counties(_df, state) -> pd.DataFrame:
    """
    A support function that will return the entries in a provided dataframe that match the provided state.  The state value provided is not case sensitive.

    :param _df:  The initial dataframe that will be filtered.
    :param state: The state string name that will be used to filter the dataframe.

    :return: A dataframe that includes the entries of the provided dataframe that only include the provided state.
    """
    return _df[_df.Province_State.str.lower() == state.lower()]


def get_rankings(_df, top_n=None) -> list:
    """
    Support function that will return a list of the top n listings in a dataframe based on the most recent date.  Results are listing in descending order.  If no top_n value is provided, all items in the dataframe are sorted.

    :param _df:  The dataframe that will be filtered and sorted.
    :param top_n: (optional) An integer value that will restrict the returned list to the top n number of listings.

    :return: A list of top_n indexes from a dataframe
    """
    attr_cols, date_cols_text, date_cols_dates = get_column_groups(_df)
    a_cols = [c for c in _df.columns if c in attr_cols]

    rv_df = _df[date_cols_text].rank(ascending=False)
    rv_df = pd.concat([_df.loc[rv_df.index][a_cols], rv_df], axis=1)

    if top_n is not None:
        return rv_df.nsmallest(top_n, date_cols_text[-1]).sort_values(by=date_cols_text[-1], ascending=True)

    return rv_df.sort_values(by=date_cols_text[-1])


# get data per day
def get_by_day(_df):
    """
    Return a dataframe that contains cumulative values in date columns in a daily value format.

    :param _df:  A dataframe where the values in each date column are cumulative values.

    :return: The supplied dataframe with daily data instead of cumulative data.
    """
    _, date_cols_text, _ = get_column_groups(_df)
    daily = _df[date_cols_text] - _df[date_cols_text].shift(axis=1)
    attr_cols = set(_df.columns) - set(date_cols_text)
    daily = pd.concat([_df[attr_cols], daily], axis=1)

    return daily


def get_daily_growth_rate(_df):
    """
    Return a dataframe that includes values that represent the change rate vs the prior day for all values in date columns.

    :param _df:  A dataframe of cumulative values in date columns

    :return: A dataframe with the same columns and rows as the original dataframe, except the values are daily change rates rather than cumulative absolute values.
    """
    _, date_cols_text, _ = get_column_groups(_df)
    _df = get_by_day(_df)
    daily_rate = _df[date_cols_text] / _df[date_cols_text].shift(axis=1)
    attr_cols = set(_df.columns) - set(date_cols_text)
    daily_rate = pd.concat([_df[attr_cols], daily_rate], axis=1)
    daily_rate = daily_rate.fillna(1)
    return daily_rate
