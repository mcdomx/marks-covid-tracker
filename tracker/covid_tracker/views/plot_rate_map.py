# import os
#
# from shapely.geometry import Polygon
# from bokeh.models import LinearColorMapper
# from bokeh.models import RadioGroup, Slider, Div, Spacer, Select
# from bokeh.plotting import figure
# from bokeh.models import FactorRange, ColumnDataSource, HoverTool, NumeralTickFormatter
# from bokeh.layouts import column, row
# from bokeh.palettes import RdYlGn
#
#
# home_dir = os.getenv("HOME")
# data_dir = os.path.join(home_dir, ".bokeh", "data")
# counties_file = os.path.join(home_dir, ".bokeh", "data", "US_Counties.csv")
#
# if not os.path.isfile(counties_file):
#     import bokeh.sampledata
#     bokeh.sampledata.download()
#
# from bokeh.sampledata.us_counties import data as counties
#
# from covid_webapp.helpers import *
#
#
# # Get GeoPandas DF with the regions of each county
# def add_county_geometry(df):
#     cts = pd.DataFrame(counties).T
#
#     def extract_state(s):
#         county, state = s['detailed name'].split(',')
#         return state.strip()
#
#     cts['Province_State'] = cts.apply(extract_state, axis=1)
#
#     cts['geometry'] = cts.apply(lambda s: Polygon([(x, y) for x, y in zip(s.lons, s.lats)]), axis=1)
#     counties_gpd = gpd.GeoDataFrame(cts, geometry='geometry')
#
#     counties_gpd = counties_gpd.rename(columns={'name': 'County'})
#     counties_gpd = counties_gpd.rename(columns={'detailed name': 'County_State'})
#     counties_gpd['County_State'] = [f"{c}, {s}" for c, s in
#                                     zip(counties_gpd.County.values, counties_gpd.Province_State)]
#
#     # remove territories
#     counties_gpd = counties_gpd[~counties_gpd.Province_State.isin(territories)]
#
#     # remove alaska and hawaii to plot them
#     counties_gpd = counties_gpd[(counties_gpd.Province_State != "Alaska") & (counties_gpd.Province_State != "Hawaii")]
#
#     # merge the county regions with the dataframe that has the data to plot
#     df = counties_gpd[['County_State', 'lats', 'lons']].merge(df.drop(columns='geometry'), on='County_State')
#
#     # remove out-of-state entries
#     df = df[(df.Lat != 0) & (df.Long_ != 0)]
#
#     return df
#
#
# def plot_map(days_trend=7, days_ago=1, data_type='Infections'):
#     # set dataframes
#     confirmed_us_df = add_county_geometry(get_dataframe('confirmed_US'))
#     deaths_us_df = add_county_geometry(get_dataframe('deaths_US'))
#
#     # setup Hover tool
#     hover = HoverTool()
#     hover.tooltips = [
#         ("Name", "@name"),
#         (f"{days_ago}-Day Infection Rate", "@rate"),
#     ]
#
#     TOOLS = ['pan', 'wheel_zoom', 'reset', hover]
#     palette = tuple((RdYlGn[10]))
#     color_mapper = LinearColorMapper(palette=palette, low=.9, high=1.9)
#
#     def get_plot(_df):
#
#         county_xs = _df["lons"].to_list()
#         county_ys = _df["lats"].to_list()
#         county_names = _df['County_State'].to_list()
#
#         # get mean growth rate over window period for most recent reporting date
#         county_rates = get_daily_growth_rate(_df).rolling(days_trend, axis=1).mean().fillna(1).iloc[:, -1].to_list()
#
#         day_word = "Day" if days_trend < 1 else "Days"
#         p = figure(
#             plot_width=900,
#             #         plot_height=500,
#             title=f"COVID Weekly Infection {days_trend}-Day Rate ({days_ago} {day_word} Ago)",
#             tools=TOOLS,
#             x_axis_location=None, y_axis_location=None,
#         )
#         p.grid.grid_line_color = None
#         p.hover.point_policy = "follow_mouse"
#
#         data = dict(
#             x=county_xs,
#             y=county_ys,
#             name=county_names,
#             rate=county_rates,
#         )
#
#         patches = p.patches('x', 'y', source=data,
#                             fill_color={'field': 'rate', 'transform': color_mapper},
#                             fill_alpha=0.7, line_color="white", line_width=0.2)
#
#         return p, patches
#
#     plot, patches = get_plot(_df=confirmed_us_df if data_type == 'Infections' else deaths_us_df)
#
#     def update_map(_state, _days_trend, _data_type, _days_ago):
#
#         _df = confirmed_us_df if _data_type == 'Infections' else deaths_us_df
#
#         day_word = "Day" if _days_trend < 1 else "Days"
#         if _data_type == "Infections":
#             layout.children[
#                 2].title.text = f"COVID Weekly {_days_trend}-Day Infection Rate ({_days_ago} {day_word} Ago)"
#             hover.tooltips = [
#                 ("Name", "@name"),
#                 (f"{_days_trend}-Day Infection Rate", "@rate"),
#             ]
#
#         elif _data_type == "Deaths":
#             layout.children[2].title.text = f"COVID Weekly {_days_trend}-Day Death Rate ({_days_ago} {day_word} Ago)"
#             hover.tooltips = [
#                 ("Name", "@name"),
#                 (f"{_days_trend}-Day Death Rate", "@rate{0,0.000}"),
#             ]
#
#         if _state == 'US':
#             df_updated = _df
#         else:
#             df_updated = _df[_df.Province_State == _state]
#
#         data = dict(
#             x=df_updated["lons"].to_list(),
#             y=df_updated["lats"].to_list(),
#             name=df_updated['County_State'].to_list(),
#             rate=get_daily_growth_rate(df_updated).rolling(_days_trend, axis=1).mean().fillna(1).iloc[:,
#                  -_days_ago].to_list(),
#         )
#
#         patches.data_source.data = data
#
#     # Chart controls
#     state_menu = [('US', 'US')] + [(s, s) for s in list(confirmed_us_df.Province_State.unique())]
#     state_dd = Select(title="Choose state:", value='US', options=state_menu)
#
#     def state_change(attr, old, new):
#         update_map(_state=new,
#                    _days_trend=trend_slider.value,
#                    _data_type=data_group.labels[data_group.active],
#                    _days_ago=daysago_slider.value
#                    )
#
#     state_dd.on_change('value', state_change)
#
#     trend_slider = Slider(start=1, end=21, value=days_trend, step=1, title="Trend Days", value_throttled=True)
#
#     def trend_slider_change(attr, old, new):
#         update_map(_state=state_dd.value,
#                    _days_trend=new,
#                    _data_type=data_group.labels[data_group.active],
#                    _days_ago=daysago_slider.value)
#
#     trend_slider.on_change('value_throttled', trend_slider_change)
#
#     daysago_slider = Slider(start=1, end=21, value=1, step=1, title="Days Ago", value_throttled=True)
#
#     def daysago_slider_change(attr, old, new):
#         update_map(_state=state_dd.value,
#                    _days_trend=trend_slider.value,
#                    _data_type=data_group.labels[data_group.active],
#                    _days_ago=new)
#
#     daysago_slider.on_change('value_throttled', daysago_slider_change)
#
#     data_group = RadioGroup(labels=["Infections", "Deaths"], active=0)
#
#     def data_change(attr, old, new):
#         update_map(_state=state_dd.value,
#                    _days_trend=trend_slider.value,
#                    _data_type=data_group.labels[new],
#                    _days_ago=daysago_slider.value)
#
#     data_group.on_change('active', data_change)
#
#     controls_layout = column(children=[state_dd,
#                                        row(Spacer(height=15)),
#                                        trend_slider,
#                                        row(Spacer(height=15)),
#                                        daysago_slider,
#                                        row(Spacer(height=15)),
#                                        Div(text="""<b>Data Type:</b>"""), row(Spacer(width=15), data_group)], width=200)
#
#     layout = row(children=[controls_layout, Spacer(width=15), plot])
#
#     return layout
