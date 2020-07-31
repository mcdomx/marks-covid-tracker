import git
import json


from django.shortcuts import render
from django.http import JsonResponse

from .helpers import *


# Create your views here.
# def plot_state_chart(request, state="United States", county='All', frequency='daily', data_type='infections', rolling_window=14):
#     """Plots single area.  Give a single row."""
#     if request is not None:
#         state = request.GET.get('state', 'United States')
#         county = request.GET.get('county', 'All')
#         frequency = request.GET.get('frequency', 'daily')
#         data_type = request.GET.get('data_type', 'infections').lower()
#         rolling_window = int(request.GET.get('rolling_window', 14))
#
#     state = ' '.join([word.capitalize() for word in state.split(' ')])
#     county = county.capitalize()
#
#     # for p in [state, county, frequency, data_type, rolling_window]:
#     #     print(p)
#
#     # set dataframes
#     confirmed_us_df = get_dataframe('confirmed_US')
#     deaths_us_df = get_dataframe('deaths_US')
#
#     if data_type == 'infections':
#         df = confirmed_us_df
#     else:
#         df = deaths_us_df
#
#     if frequency == 'daily':
#         all_data = get_by_day(df)
#     else:
#         all_data = df.copy()
#
#     if state == 'United States':
#         plot_data = all_data.sum()[DATE_COLS_TEXT].values
#     else:
#         if county == 'All':
#             plot_data = all_data[all_data.Province_State == state].sum()[DATE_COLS_TEXT].values
#         else:
#             plot_data = all_data[(all_data.Province_State == state) & (all_data.County == county)].sum()[
#                 DATE_COLS_TEXT].values
#
#     # setup x axis groupings
#     factors = [(c.month_name(), str(c.day)) for c in DATE_COLS_DATES]
#
#     # setup Hover tool
#     hover = HoverTool()
#     hover.tooltips = [
#         ("Date", "@date"),
#         (data_type, "@val"),
#         (f"{rolling_window}-day Avg", "@rolling_avg{0,0.0}")
#     ]
#
#     # setup figure
#     p = figure(x_range=FactorRange(*factors), plot_height=500, plot_width=900,
#                y_axis_type='linear', y_axis_label=data_type,
#                toolbar_location=None, tools=[hover], title=f"{state} New {data_type.capitalize()}{' by Day' if frequency == 'daily' else ''}")
#     p.title.text_font_size = '12pt'
#     p.yaxis.formatter = NumeralTickFormatter(format="0,000")
#
#     source = ColumnDataSource(
#         data=dict(date=factors, val=plot_data, rolling_avg=pd.Series(plot_data).rolling(rolling_window).mean().values))
#
#     b = p.vbar(x='date', top='val', source=source, color='red', width=.5)
#
#     if frequency == 'daily':
#         l = p.line(x='date', y='rolling_avg', source=source, color='black', width=3, legend_label=f"{rolling_window}-Day Rolling Average")
#         p.legend.location = 'top_left'
#
#     p.xaxis.major_label_orientation = 1
#     p.xaxis.group_text_font_size = "10pt"  # months size
#     p.xaxis.major_label_text_font_size = "6pt"  # date size
#     p.yaxis.major_label_orientation = 1
#     p.xgrid.grid_line_color = None
#
#     return JsonResponse(json_item(p))


def get_states(request):
    df = get_dataframe('confirmed_US')
    states = ['United States'] + list(df.Province_State.unique())
    return JsonResponse(states, safe=False)


def refresh_git(request):
    g = git.cmd.Git('COVID-19')
    print(g.working_dir)
    g.pull()
    g.fetch()
    g.refresh()
    # print(os.getcwd())
    # os.system("cd COVID-19; git pull; cd ..")
    return JsonResponse("Git refreshed", safe=False)


def get_counties(request):
    state = request.GET.get('state')
    df = get_dataframe('confirmed_US')
    _counties_in_state = ['All'] + list(df[df.Province_State == state].County.unique())
    return JsonResponse(_counties_in_state, safe=False)


def index_view(request):
    """
    Default Index route which shows the initial page
    :param request:
    :return:
    """

    region_df = get_dataframe('confirmed_US')[['Province_State', 'County']]

    # states = ['United States'] + list(df.Province_State.unique())
    region_melt = pd.melt(region_df, id_vars='Province_State', value_vars='County')[['Province_State', 'value']]
    states = region_melt['Province_State'].to_list()

    region_dict = {"United States": ["All"]}
    for s in states:
        counties = ['All'] + region_melt[region_melt['Province_State'] == s]['value'] .to_list()
        region_dict.update({s: counties})

    return render(request, 'covid_tracker/home.html', {"states": json.dumps(region_dict)})
