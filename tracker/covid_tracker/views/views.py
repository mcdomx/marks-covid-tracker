import os
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.models import Select, RadioGroup, Slider, Div, Spacer
from bokeh.layouts import column, row

from django.shortcuts import render

from .helpers import *

# Create your views here.
def plot_total_infections(state="Massachusetts", by_day=False, rolling_window=14):
    """Plots single area.  Give a single row."""

    # defaults
    data_type = 'Infections'

    # set dataframes
    confirmed_us_df = get_dataframe('confirmed_US')
    deaths_us_df = get_dataframe('deaths_US')
    df = confirmed_us_df

    if by_day:
        all_data = get_by_day(df)
    else:
        all_data = df.copy()

    plot_data = all_data[all_data.Province_State == state].sum()[DATE_COLS_TEXT].values

    # setup x axis groupings
    factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]

    # setup Hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Date", "@date"),
        ("Infections", "@val"),
        (f"{rolling_window}-day Avg", "@rolling_avg{0,0.0}")
    ]

    # setup figure
    p = figure(x_range=FactorRange(*factors), plot_height=500, plot_width=900,
               y_axis_type='linear', y_axis_label=data_type,
               toolbar_location=None, tools=[hover], title=f"New Infections{' by Day' if by_day else ''}")
    p.yaxis.formatter = NumeralTickFormatter(format="0,000")

    source = ColumnDataSource(
        data=dict(date=factors, val=plot_data, rolling_avg=pd.Series(plot_data).rolling(rolling_window).mean().values))

    b = p.vbar(x='date', top='val', source=source, color='red', width=.5)

    if by_day:
        l = p.line(x='date', y='rolling_avg', source=source, color='black', width=3, legend_label=f"Rolling Average")
        p.legend.location = 'top_left'

    p.xaxis.major_label_orientation = 1
    p.xaxis.group_text_font_size = "10pt"  # months size
    p.xaxis.major_label_text_font_size = "6pt"  # date size
    p.yaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    # Update the values when widgets are changed
    def update_chart(_state=state, _county='All', _rolling_window=rolling_window, _by_day=by_day, _data_type=data_type):

        _df = confirmed_us_df if _data_type == 'Infections' else deaths_us_df
        p.yaxis.axis_label = _data_type

        if _data_type == "Infections":
            p.title.text = f"New Infections {'by Day' if _by_day else 'Cumulative'}"
            hover.tooltips = [
                ("Date", "@date"),
                ("Infections", "@val"),
                (f"{_rolling_window}-day Avg", "@rolling_avg{0,0.0}")
            ]
        elif _data_type == "Deaths":
            p.title.text = f"Deaths {'by Day' if _by_day else 'Cumulative'}"
            hover.tooltips = [
                ("Date", "@date"),
                ("Deaths", "@val"),
                (f"{_rolling_window}-day Avg", "@rolling_avg{0,0.0}")
            ]

        if _by_day:
            all_data = get_by_day(_df)
        else:
            all_data = _df.copy()

        if _county != 'All':
            plot_data = all_data[(all_data.Province_State == _state) & (all_data.County == _county)].sum()[
                DATE_COLS_TEXT].values
        else:
            plot_data = all_data[all_data.Province_State == _state].sum()[DATE_COLS_TEXT].values

        b.data_source.data['val'] = plot_data
        if _by_day:
            l.data_source.data['rolling_avg'] = pd.Series(plot_data).rolling(_rolling_window).mean().values

    # Chart controls
    state_menu = [(s, s) for s in list(df.Province_State.unique())]
    state_dd = Select(title="Choose state:", value='Massachusetts', options=state_menu)

    counties_in_state = ['All'] + list(df[df.Province_State == 'Massachusetts'].County.unique())
    county_menu = [(c, c) for c in counties_in_state]
    county_dd = Select(title="Choose county:", value='All', options=county_menu)

    def state_change(attr, old, new):
        _counties_in_state = ['All'] + list(df[df.Province_State == new].County.unique())
        _county_menu = [(c, c) for c in _counties_in_state]
        county_dd.options = _county_menu
        county_dd.value = 'All'
        update_chart(_state=new, _county='All',
                     _rolling_window=window_slider.value,
                     _by_day=True if freq_group.labels[freq_group.active] == 'Daily' else False,
                     _data_type=data_group.labels[data_group.active])

    state_dd.on_change('value', state_change)

    def county_change(attr, old, new):
        update_chart(_state=state_dd.value,
                     _county=new,
                     _rolling_window=window_slider.value,
                     _by_day=True if freq_group.labels[freq_group.active] == 'Daily' else False,
                     _data_type=data_group.labels[data_group.active])

    county_dd.on_change('value', county_change)

    window_slider = Slider(start=1, end=21, value=rolling_window, step=1, title="Rolling Window Days")

    def slider_change(attr, old, new):
        update_chart(_state=state_dd.value,
                     _county=county_dd.value,
                     _rolling_window=new,
                     _by_day=True if freq_group.labels[freq_group.active] == 'Daily' else False,
                     _data_type=data_group.labels[data_group.active])

    window_slider.on_change('value', slider_change)

    freq_group = RadioGroup(labels=["Daily", "Cumulative"], active=0)

    def freq_change(attr, old, new):
        update_chart(_state=state_dd.value,
                     _county=county_dd.value,
                     _rolling_window=window_slider.value,
                     _by_day=True if freq_group.labels[new] == 'Daily' else False,
                     _data_type=data_group.labels[data_group.active])

    freq_group.on_change('active', freq_change)

    data_group = RadioGroup(labels=["Infections", "Deaths"], active=0)

    def data_change(attr, old, new):
        update_chart(_state=state_dd.value,
                     _county=county_dd.value,
                     _rolling_window=window_slider.value,
                     _by_day=True if freq_group.labels[freq_group.active] == 'Daily' else False,
                     _data_type=data_group.labels[new])

    data_group.on_change('active', data_change)

    controls_layout = column(children=[state_dd, county_dd,
                                       row(Spacer(height=15)),
                                       window_slider,
                                       row(Spacer(height=15)),
                                       Div(text="""<b>Frequency:</b>"""), row(Spacer(width=15), freq_group),
                                       Div(text="""<b>Data Type:</b>"""), row(Spacer(width=15), data_group)], width=200)

    layout = row(controls_layout, Spacer(width=15), p)

    return components(layout)


def index_view(request):
    """
    Default Index route which shows the initial page
    :param request:
    :return:
    """

    div, script = plot_total_infections()

    return render(request, 'covid_tracker/home.html', {'div': div, 'script': script})
