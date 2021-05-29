
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter, CustomLabelingPolicy
from bokeh.models.callbacks import CustomJS

from django.http import JsonResponse

from .helpers import *


def _get_plot_data(data_type, frequency, state, county):
    # set dataframes
    if data_type == 'infections':
        df_dict = get_dataframe('confirmed_US')
    else:
        df_dict = get_dataframe('deaths_US')

    # _, date_cols_text, date_cols_dates = get_column_groups(df)

    df = df_dict['df']
    date_cols_text = df_dict['date_cols_text']
    date_cols_dates = df_dict['date_cols_dates']

    if frequency == 'daily':
        all_data = get_by_day(df)
    else:
        all_data = df.copy()

    if state == 'United States':
        plot_data = all_data.sum()[date_cols_text].values
    else:
        if county == 'All':
            plot_data = all_data[all_data.Province_State == state].sum()[date_cols_text].values
        else:
            plot_data = all_data[(all_data.Province_State == state) & (all_data.County == county)].sum()[
                date_cols_text].values

    # setup x axis groupings
    factors = [(str(c.year), c.month_name(), str(c.day)) for c in date_cols_dates]

    # return plot_data[-365:], factors[-365:]
    return plot_data, factors


def plot_state_chart(request, state="United States", county='All', frequency='daily', data_type='infections', rolling_window=14):
    """
    Plots the values for a selected state, county or the entire United States.

    :param request:  The HTML request that should include values for 'state', 'county', 'frequency', 'data_type' and 'rolling_window'.  See the parameter descriptions below for contraints and defaults for each parameter.
    :param state: (optional) Default 'Massachusetts'.  The name of the state to plot.
    :param county: (optional) Default 'All'.  The county to plot or 'All' counties of a state of value is 'All'.
    :param frequency: (optional) Default 'daily'.  Whether to plot daily or cumulative values.
    :param data_type: (optional) Default 'infections'.  Plot 'infections' data or 'deaths' data.
    :param rolling_window: (optional) Default 14.  The number of days to use when drawing the daily average line in the plot.

    :return: A Bokeh JSON formatted plot that can be handled by JavaScript for HTML presentation.
    """
    if request is not None:
        state = request.GET.get('state', 'United States')
        county = request.GET.get('county', 'All')
        frequency = request.GET.get('frequency', 'daily')
        data_type = request.GET.get('data_type', 'infections').lower()
        rolling_window = int(request.GET.get('rolling_window', 14))

    state = ' '.join([word.capitalize() for word in state.split(' ')])
    county = county.capitalize()

    plot_data, factors = _get_plot_data(data_type, frequency, state, county)

    # # setup x axis groupings
    # factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]

    # setup Hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Date", "@date"),
        (data_type.capitalize(), "@val{0,0}"),
        (f"{rolling_window}-day Avg", "@rolling_avg{0,0.0}")
    ]

    # setup figure
    p = figure(x_range=FactorRange(*factors), sizing_mode='stretch_both',  # plot_height=500, plot_width=900,
               y_axis_type='linear', y_axis_label=data_type, output_backend="webgl",
               toolbar_location=None, tools=[hover], id="state_totals",
               title=f"{state} New {data_type.capitalize()}{' by Day' if frequency == 'daily' else ''}")
    p.title.text_font_size = '12pt'
    p.yaxis.formatter = NumeralTickFormatter(format="0,000")

    source = ColumnDataSource(
        data=dict(date=factors, val=plot_data, rolling_avg=pd.Series(plot_data).rolling(rolling_window).mean().values))

    b = p.vbar(x='date', top='val', source=source, color='red', width=.5)

    if frequency == 'daily':
        l = p.line(x='date', y='rolling_avg', source=source, color='black', width=3, legend_label=f"{rolling_window}-Day Rolling Average")
        p.legend.location = 'top_left'

    p.xaxis.major_label_orientation = 1
    p.xaxis.group_text_font_size = "10pt"  # months size
    p.xaxis.major_label_text_font_size = "3pt"  # date size
    p.xaxis.major_tick_line_color = None

    # p.xaxis.visible = False  # hide the dates
    p.yaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    callback = CustomJS(args=dict(source=source), code="""

        // JavaScript code goes here

        var updated_data; 

        // the model that triggered the callback is cb_obj:
        fetch(cb_obj.value)
        .then( response = return response.json() )
        .then( x => udpated_data = x ) 

        // models passed as args are automagically available
        source.data = updated_data;

        """)

    return JsonResponse(json_item(p))
