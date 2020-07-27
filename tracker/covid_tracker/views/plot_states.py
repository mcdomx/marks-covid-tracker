from bokeh.plotting import figure
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.models import RadioGroup, Slider, Div, Spacer, Select, MultiSelect
from bokeh.layouts import column, row
from bokeh.palettes import Category20

from covid_webapp.helpers import *


def plot_confirmed_by_state(states=None, top_n=15, skip_states: list = None):

    # make sure the top_n is between 3 and 20
    if top_n < 3:
        top_n = 3
    elif top_n > 20:
        top_n = 20

    # defaults
    data_type = 'Infections'

    # set dataframes
    confirmed_us_df = get_dataframe('confirmed_US')
    deaths_us_df = get_dataframe('deaths_US')

    def get_df(_data_type, _top_n, _excl_states):
        _df = get_df_by_state(confirmed_us_df if _data_type == 'Infections' else deaths_us_df)
        rankings = get_rankings(_df, top_n=_top_n)
        _df = _df.loc[rankings.index]

        if _excl_states:
            _df = _df[~_df.Province_State.isin(_excl_states)]

        return _df

    df = get_df(_data_type=data_type, _top_n=top_n, _excl_states=None)

    states = df.Province_State.unique()

    factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]

    hover = HoverTool()
    hover.tooltips = [
        ("State", "@state"),
        ("Date", "@date"),
        ("Infections", "@val{0,0}"),
        ("Rank", "@ranking"),
    ]

    def get_plot(_df=df, _hover=hover):
        p = figure(x_range=FactorRange(*factors), plot_height=500, plot_width=900,
                   y_axis_type='linear',  y_axis_label=data_type,
                   toolbar_location=None, tools=[hover], title="Confirmed Cases by State")
        p.yaxis.formatter = NumeralTickFormatter(format="0,000")

        for i, state in enumerate(states):
            # if skip_states and state in skip_states: continue
            try:
                source = ColumnDataSource(data=dict(date=factors,
                                                    state=[state] * len(factors),
                                                    val=_df[_df.Province_State == state][DATE_COLS_TEXT].values[0],
                                                    ranking=_df[DATE_COLS_TEXT].rank(ascending=False)[
                                                        _df.Province_State == state].values[0])
                                          )
            except:
                continue

            p.line('date', 'val', source=source, color=Category20[top_n][i], line_width=2, legend_label=state)
            p.legend.location = 'top_left'
            p.legend.label_text_font_size = '6pt'
            p.legend.orientation = "vertical"
            p.legend.padding = 1
            p.legend.title = 'State'
            p.y_range.start = 0
            p.xaxis.major_label_orientation = 1
            p.xaxis.group_text_font_size = "10pt"  # months size
            p.xaxis.major_label_text_font_size = "6pt"  # date size
            p.yaxis.major_label_orientation = 1
            p.xgrid.grid_line_color = None
        return p

    plot = get_plot()

    # Update the values when widgets are changed
    def update_chart(_excl_states=None, _data_type=data_type, _top_n=top_n):

        _df = get_df(_data_type=_data_type, _top_n=_top_n, _excl_states=_excl_states)
        layout.children[2] = get_plot(_df)
        layout.children[2].yaxis.axis_label = _data_type

        if _data_type == "Infections":
            layout.children[2].title.text = f"Cumulative New Infections by State"
            hover.tooltips = [
                ("State", "@state"),
                ("Date", "@date"),
                ("Infections", "@val"),
                ("Rank", "@ranking"),
            ]
        elif _data_type == "Deaths":
            layout.children[2].title.text = f"Cumulative Deaths by Day by State"
            hover.tooltips = [
                ("State", "@state"),
                ("Date", "@date"),
                ("Deaths", "@val"),
                ("Rank", "@ranking"),
            ]

    # Chart controls
    state_menu = [(s, s) for s in list(confirmed_us_df.Province_State.unique())]
    state_dd = MultiSelect(title="Exclude States:", value=None, options=state_menu)
    state_dd.size = 20

    def state_change(attr, old, new):
        update_chart(_excl_states=state_dd.value,
                     _data_type=data_group.labels[data_group.active],
                     _top_n=top_slider.value
                     )

    state_dd.on_change('value', state_change)

    data_group = RadioGroup(labels=["Infections", "Deaths"], active=0)

    def data_change(attr, old, new):
        update_chart(_excl_states=state_dd.value,
                     _data_type=data_group.labels[new],
                     _top_n=top_slider.value
                     )

    data_group.on_change('active', data_change)

    top_slider = Slider(start=1, end=20, value=top_n, step=1, title="Top n States")

    def slider_change(attr, old, new):
        update_chart(_excl_states=state_dd.value,
                     _data_type=data_group.labels[data_group.active],
                     _top_n=new
                     )

    top_slider.on_change('value', slider_change)

    controls_layout = column(children=[state_dd,
                                       row(Spacer(height=15)),
                                       top_slider,
                                       row(Spacer(height=15)),
                                       Div(text="""<b>Data Type:</b>"""), row(Spacer(width=15), data_group)], width=200)

    layout = row(children=[controls_layout, Spacer(width=15), plot])

    return layout
