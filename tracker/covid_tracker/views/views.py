import git
import json


from django.shortcuts import render
from django.http import JsonResponse

from .helpers import *


# Create your views here.

def get_states(request):
    df = get_dataframe('confirmed_US')
    states = ['United States'] + list(df.Province_State.unique())
    return JsonResponse(states, safe=False)


def refresh_git(request):
    g = git.cmd.Git('covid_tracker/COVID-19')
    g.pull()
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
