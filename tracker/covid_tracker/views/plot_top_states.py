
from bokeh.palettes import Category20
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter

from django.http import JsonResponse

from .helpers import *


def _get_plot_data(_data_type, _top_n, _exclude_states):

    if _data_type == 'infections':
        df = get_df_by_state(get_dataframe('confirmed_US'))
    else:
        df = get_df_by_state(get_dataframe('deaths_US'))

    rankings = get_rankings(df, top_n=_top_n)
    df = df.loc[rankings.index]

    if _exclude_states:
        df = df[~df.Province_State.isin(_exclude_states)]

    return df


def plot_top_states(request, states=None, top_n_states=15, data_type='infections', exclude_states: list = None):

    top_n = top_n_states

    if request is not None:
        states = request.GET.get('states', None)
        data_type = request.GET.get('data_type', 'infections').lower()
        top_n = int(request.GET.get('top_n_states', 15))
        exclude_states = request.GET.get('exclude_states', False)

    if states is 'null':
        states = None
    if exclude_states is 'null':
        exclude_states = False

    # make sure the top_n is between 3 and 20
    if top_n < 3:
        top_n = 3
    elif top_n > 20:
        top_n = 20

    # df = get_df_by_state(get_dataframe('confirmed_US') if data_type == 'infections' else get_dataframe('deaths_US'))
    # rankings = get_rankings(df, top_n=top_n)
    # df = df.loc[rankings.index]
    #
    # if exclude_states:
    #     df = df[~df.Province_State.isin(exclude_states)]

    df = _get_plot_data(data_type, top_n, exclude_states)

    states = df.Province_State.unique()

    factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]

    hover = HoverTool()
    hover.tooltips = [
        ("State", "@state"),
        ("Date", "@date"),
        (f"{data_type.capitalize()}", "@val{0,0}"),
        ("Rank", "@ranking"),
    ]

    p = figure(x_range=FactorRange(*factors), sizing_mode='stretch_both',  # plot_height=500, plot_width=900,
               y_axis_type='linear',  y_axis_label=data_type, output_backend="webgl",
               toolbar_location=None, tools=[hover], title=f"Cumulative {data_type.capitalize()} by State")
    p.title.text_font_size = '12pt'
    p.yaxis.formatter = NumeralTickFormatter(format="0,000")

    for i, state in enumerate(states):
        # if skip_states and state in skip_states: continue
        try:
            source = ColumnDataSource(data=dict(date=factors,
                                                state=[state] * len(factors),
                                                val=df[df.Province_State == state][DATE_COLS_TEXT].values[0],
                                                ranking=df[DATE_COLS_TEXT].rank(ascending=False)[
                                                    df.Province_State == state].values[0])
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

    return JsonResponse(json_item(p))
