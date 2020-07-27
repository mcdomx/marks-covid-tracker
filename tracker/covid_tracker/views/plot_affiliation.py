
from bokeh.plotting import figure
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.models import RadioGroup, Slider, Div, Spacer
from bokeh.layouts import column, row

from covid_webapp.helpers import *


def plot_affiliation(by_day=True, rolling_window=14, exclude_states=[]):
    """Plots single area.  Give a single row."""

    # defaults
    data_type = 'Infections'

    confirmed_us_df = get_dataframe('confirmed_US')
    deaths_us_df = get_dataframe('deaths_US')
    df = confirmed_us_df

    if by_day:
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
        ("Infections", "@val{0,0}"),
        (f"{rolling_window}-day Avg", "@rolling_avg{0,0.0}")
    ]

    # setup figure
    p = figure(x_range=FactorRange(*factors), plot_height=500, plot_width=900, y_axis_label=data_type,
               toolbar_location=None, tools=[hover], title=f"New Infections{' by Day' if by_day else ''}")
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

    if by_day:
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

    def update_chart(_rolling_window=rolling_window, _by_day=by_day, _data_type=data_type):

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

        plot_data_red = \
        all_data[(~all_data.Province_State.isin(exclude_states)) & (all_data.political_affiliation == 'red')].sum()[
            DATE_COLS_TEXT].values
        plot_data_blue = \
        all_data[(~all_data.Province_State.isin(exclude_states)) & (all_data.political_affiliation == 'blue')].sum()[
            DATE_COLS_TEXT].values
        plot_data_purple = \
        all_data[(~all_data.Province_State.isin(exclude_states)) & (all_data.political_affiliation == 'purple')].sum()[
            DATE_COLS_TEXT].values

        b_red.data_source.data['val'] = plot_data_red
        b_blue.data_source.data['val'] = plot_data_blue

        if by_day:
            l_red.data_source.data['rolling_avg'] = pd.Series(plot_data_red).rolling(_rolling_window).mean().values
            l_blue.data_source.data['rolling_avg'] = pd.Series(plot_data_blue).rolling(_rolling_window).mean().values
            l_purple.data_source.data['rolling_avg'] = pd.Series(plot_data_purple).rolling(_rolling_window).mean().values

    window_slider = Slider(start=1, end=21, value=rolling_window, step=1, title="Rolling Window Days")

    def slider_change(attr, old, new):
        update_chart(_rolling_window=new,
                     _by_day=True if freq_group.labels[freq_group.active] == 'Daily' else False,
                     _data_type=data_group.labels[data_group.active])

    window_slider.on_change('value', slider_change)

    freq_group = RadioGroup(labels=["Daily", "Cumulative"], active=0)

    def freq_change(attr, old, new):
        update_chart(_rolling_window=window_slider.value,
                     _by_day=True if freq_group.labels[new] == 'Daily' else False,
                     _data_type=data_group.labels[data_group.active])

    freq_group.on_change('active', freq_change)

    data_group = RadioGroup(labels=["Infections", "Deaths"], active=0)

    def data_change(attr, old, new):
        update_chart(_rolling_window=window_slider.value,
                     _by_day=True if freq_group.labels[freq_group.active] == 'Daily' else False,
                     _data_type=data_group.labels[new])

    data_group.on_change('active', data_change)

    controls_layout = column(children=[window_slider,
                                       row(Spacer(height=15)),
                                       Div(text="""<b>Frequency:</b>"""), row(Spacer(width=15), freq_group),
                                       Div(text="""<b>Data Type:</b>"""), row(Spacer(width=15), data_group)], width=200)

    layout = row(controls_layout, Spacer(width=15), p)
    # curdoc().add_root(layout)

    return layout
