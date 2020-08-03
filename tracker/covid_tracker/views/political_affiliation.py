
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter

from django.http import JsonResponse

from .helpers import *


def plot_affiliation(request, frequency='daily', rolling_window=14, exclude_states=[], data_type='infections'):
    """Plots single area.  Give a single row."""

    if request is not None:
        frequency = request.GET.get('frequency', 'infections').lower()
        rolling_window = int(request.GET.get('rolling_window', 15))
        exclude_states = request.GET.get('exclude_states', False)
        data_type = request.GET.get('data_type', 'infections').lower()

    if exclude_states == 'null':
        exclude_counties = False

    # for p in [frequency, rolling_window, exclude_states, data_type]:
    #     print(p)

    df = get_dataframe('confirmed_US') if data_type == 'infections' else get_dataframe('deaths_US')

    if frequency == 'daily':
        all_data = get_by_day(df)
    else:
        all_data = df.copy()

    plot_data_red = all_data[all_data.political_affiliation == 'red'].sum()[DATE_COLS_TEXT].values
    plot_data_blue = all_data[all_data.political_affiliation == 'blue'].sum()[DATE_COLS_TEXT].values
    plot_data_purple = all_data[all_data.political_affiliation == 'purple'].sum()[DATE_COLS_TEXT].values

    # setup x axis groupings
    factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]

    # setup Hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Date", "@date"),
        (f"{data_type.capitalize()}", "@val{0,0}"),
        (f"{rolling_window}-day Avg", "@rolling_avg{0,0.0}")
    ]

    # setup figure
    p = figure(x_range=FactorRange(*factors), plot_height=500, plot_width=900, y_axis_label=data_type,
               toolbar_location=None, tools=[hover], title=f"New Infections{' by Day' if frequency=='daily' else ''}")
    p.title.text_font_size = '12pt'
    p.yaxis.formatter = NumeralTickFormatter(format="0,000")

    source_red = ColumnDataSource(data=dict(date=factors, val=plot_data_red,
                                            rolling_avg=pd.Series(plot_data_red).rolling(rolling_window).mean().values))
    source_blue = ColumnDataSource(data=dict(date=factors, val=plot_data_blue,
                                             rolling_avg=pd.Series(plot_data_blue).rolling(
                                                 rolling_window).mean().values))
    source_purple = ColumnDataSource(data=dict(date=factors, val=plot_data_purple,
                                               rolling_avg=pd.Series(plot_data_purple).rolling(
                                                   rolling_window).mean().values))

    b_red = p.vbar(x='date', top='val', source=source_red, color='red', width=.5, alpha=.5)
    b_blue = p.vbar(x='date', top='val', source=source_blue, color='blue', width=.5, alpha=.5)

    if frequency == 'daily':
        l_red = p.line(x='date', y='rolling_avg', source=source_red, color='red', width=3,
                       legend_label=f"{rolling_window}-Day Rolling Average Red")
        l_blue = p.line(x='date', y='rolling_avg', source=source_blue, color='blue', width=3,
                        legend_label=f"{rolling_window}-Day Rolling Average Blue")
        l_purple = p.line(x='date', y='rolling_avg', source=source_purple, color='purple', width=3,
                          legend_label=f"{rolling_window}-Day Rolling Average Purple")
        p.legend.location = 'top_left'

    p.xaxis.major_label_orientation = 1
    p.xaxis.group_text_font_size = "10pt"  # months size
    p.xaxis.major_label_text_font_size = "6pt"  # date size
    p.yaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    return JsonResponse(json_item(p))
