import git
import json

from django.shortcuts import render
from django.http import JsonResponse

from .helpers import *


# Create your views here.
def get_states(request):
    df = get_dataframe('confirmed_US')['df']
    states = ['United States'] + list(df.Province_State.unique())
    return JsonResponse(states, safe=False)


def refresh_git(request):
    """
    Triggers a pull of the Git repository that hold the data used in plots.

    :param request: The HTML request which is provided by Django when the route is called.  No values of the request are used in this function.

    :return: A Json formatted text response that includes the git activity of the request to pull data.
    """
    try:
        g = git.cmd.Git('covid_tracker/COVID-19')
        rv = g.pull()
    except Exception as e:
        rv = "Git sync in process..."

    print(rv)
    return JsonResponse(json.dumps(rv), safe=False)


def get_counties(request):
    """
    Provides the counties of a state.

    :param request: The HTML request which is provided by Django when the route is called.  A 'state' value is required to identify the state for which counties are returned.

    :return: A JSON formatted list of counties in the provided state.
    """
    state = request.GET.get('state')
    df = get_dataframe('confirmed_US')['df']
    _counties_in_state = ['All'] + list(df[df.Province_State == state].County.unique())
    return JsonResponse(_counties_in_state, safe=False)


def index_view(request):
    """
    Default Index route which shows the initial page.  A call to this route will attempt to refresh the Git status of the repo.
    :param request:  The HTML request which is provided by Django when the route is called.
    :return:  Renders an HTML home page with 'states' and 'political_affiliation' values available to Jinja.
    """

    # refresh git
    logging.info(refresh_git(request))

    region_df = get_dataframe('confirmed_US')['df'][['Province_State', 'County']]
    region_melt = pd.melt(region_df, id_vars='Province_State', value_vars='County')[['Province_State', 'value']]
    states = region_melt['Province_State'].to_list()

    region_dict = {"United States": ["All"]}
    for s in states:
        counties = ['All'] + region_melt[region_melt['Province_State'] == s]['value'] .to_list()
        region_dict.update({s: counties})

    return render(request, 'covid_tracker/home.html', {"states": json.dumps(region_dict),
                                                       "political_affiliations": json.dumps(political_affiliations)})
