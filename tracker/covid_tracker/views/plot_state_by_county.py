from bokeh.plotting import figure
from bokeh.palettes import Category20
from bokeh.embed import json_item
from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter

from django.http import JsonResponse

from .helpers import *


def plot_state_by_county_chart(request, state='Massachusetts', exclude_counties=False, top_n_counties=15, data_type='infections'):

    top_n = top_n_counties

    if request is not None:
        state = request.GET.get('state', 'Massachusetts')
        exclude_counties = request.GET.get('exclude_counties', False)
        top_n = int(request.GET.get('top_n_counties', 15))
        data_type = request.GET.get('data_type', 'infections').lower()

    if exclude_counties == 'null':
        exclude_counties = False

    state = ' '.join([word.capitalize() for word in state.split(' ')])

    # set dataframes
    confirmed_us_df = get_dataframe('confirmed_US')
    deaths_us_df = get_dataframe('deaths_US')

    def get_df(_state, _data_type, _top_n, _excl_counties):
        _df = get_df_by_counties(confirmed_us_df if _data_type == 'infections' else deaths_us_df, state=_state)
        rankings = get_rankings(_df, top_n=_top_n)
        _df = _df.loc[rankings.index]

        if _excl_counties:
            _df = _df[~_df.County.isin(_excl_counties)]

        return _df

    df = get_df(_state=state, _data_type=data_type, _top_n=top_n, _excl_counties=exclude_counties)

    factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]

    hover = HoverTool()
    hover.tooltips = [
        ("County", "@county"),
        ("Date", "@date"),
        (data_type.capitalize(), "@val{0,0}"),
        ("Rank", "@ranking"),
    ]

    p = figure(x_range=FactorRange(*factors), plot_height=500, plot_width=900,
               y_axis_type='linear', y_axis_label=data_type, output_backend="webgl",
               toolbar_location=None, tools=[hover], title=f"Cumulative {data_type.capitalize()} by County")
    p.title.text_font_size = '12pt'
    p.yaxis.formatter = NumeralTickFormatter(format="0,000")

    for i, county in enumerate(df.County):
        source = ColumnDataSource(data=dict(date=factors,
                                            county=[county] * len(factors),
                                            val=df[df.County == county][DATE_COLS_TEXT].values[0],
                                            ranking=
                                            df[DATE_COLS_TEXT].rank(ascending=False)[df.County == county].values[
                                                0])
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
