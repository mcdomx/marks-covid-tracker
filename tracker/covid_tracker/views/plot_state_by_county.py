from bokeh.plotting import figure
from bokeh.palettes import Category20
from bokeh.embed import json_item
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter

from django.http import JsonResponse

from .helpers import *


def _get_plot_data(_state, _data_type, _top_n, _excl_counties):

    if _data_type == 'infections':
        _df_dict = get_dataframe('confirmed_US')
    else:
        _df_dict = get_dataframe('deaths_US')

    _df_dict['df'] = get_df_by_counties(_df_dict['df'], state=_state)
    rankings = get_rankings(_df_dict['df'], top_n=_top_n)
    _df_dict['df'] = _df_dict['df'].loc[rankings.index]

    if _excl_counties:
        _df_dict['df'] = _df_dict['df'][~_df_dict['df'].County.isin(_excl_counties)]

    return _df_dict


def plot_state_by_county_chart(request, state='Massachusetts', exclude_counties=False, top_n_counties=15, data_type='infections'):
    """
    Plots a line chart of values by date for the counties in a provided state.  Not all counties are shown to avoid visual confusion.  The top_n counties defaults to 15 but can be set.  Infections are plotted by default, but 'deaths' can be plotted as well.  Counties can be excluded from the plot.
    The function can be called with parameters in a request object or with specific parameters.  If a request object is supplied, other variables supplied are ignored.

    :param request:  The HTML request that should include values for 'state', 'exclude_counties', 'top_n_counties' and 'data_type'.  See the parameter descriptions below for contraints and defaults for each parameter.
    :param state: (optional) Default 'Massachusetts'.  The name of the state to plot.
    :param exclude_counties: (optional) Default is None.  A list of counties that should be excluded from the plot.
    :param top_n_counties: (optional) Defaults to 15.  The top n counties plotted.
    :param data_type: (optional) Defaults to 'infections'.  Can also be 'deaths'.

    :return: A Bokeh JSON formatted plot that can be handled by JavaScript for HTML presentation.
    """
    top_n = top_n_counties

    if request is not None:
        state = request.GET.get('state', 'Massachusetts')
        exclude_counties = request.GET.get('exclude_counties', False)
        top_n = int(request.GET.get('top_n_counties', 15))
        data_type = request.GET.get('data_type', 'infections').lower()

    if exclude_counties == 'null':
        exclude_counties = False

    state = ' '.join([word.capitalize() for word in state.split(' ')])

    df_dict = _get_plot_data(_state=state, _data_type=data_type, _top_n=top_n, _excl_counties=exclude_counties)

    df = df_dict['df']
    date_cols_text = df_dict['date_cols_text']
    date_cols_dates = df_dict['date_cols_dates']

    factors = [(c.month_name(), str(c.day)) for c in date_cols_dates]

    hover = HoverTool()
    hover.tooltips = [
        ("County", "@county"),
        ("Date", "@date"),
        (data_type.capitalize(), "@val{0,0}"),
        ("Rank", "@ranking"),
    ]

    p = figure(x_range=FactorRange(*factors), sizing_mode='stretch_both',  # plot_height=500, plot_width=900,
               y_axis_type='linear', y_axis_label=data_type, output_backend="webgl",
               toolbar_location=None, tools=[hover], title=f"Cumulative {data_type.capitalize()} by County")
    p.title.text_font_size = '12pt'
    p.yaxis.formatter = NumeralTickFormatter(format="0,000")

    for i, county in enumerate(df.County):
        source = ColumnDataSource(data=dict(date=factors,
                                            county=[county] * len(factors),
                                            val=df[df.County == county][date_cols_text].values[0],
                                            ranking=
                                            df[date_cols_text].rank(ascending=False)[df.County == county].values[0])
                                  )

        p.line('date', 'val', source=source, color=Category20[len(df.County)][i], line_width=2,
               legend_label=county)

    p.legend.label_text_font_size = '6pt'
    p.legend.orientation = "vertical"
    p.legend.padding = 1
    p.legend.title = state
    p.legend.location = 'top_left'
    p.y_range.start = 0
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_text_font_size = "10pt"  # months size
    p.xaxis.major_label_text_font_size = "6pt"  # date size
    p.yaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    return JsonResponse(json_item(p))
