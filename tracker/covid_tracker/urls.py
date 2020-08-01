"""tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path

from .views import views
from .views import plot_state_totals
from .views import plot_state_by_county
from .views import political_affiliation
from .views import plot_top_states

urlpatterns = [
    # Default route
    path("", views.index_view, name="index"),
    path("refresh_git", views.refresh_git, name='refresh_git'),
    # path("get_states", views.get_states, name='get_states'),
    #
    # re_path('get_counties[\/|\?].*', views.get_counties, name='get_counties'),
    re_path(r"state_chart[\/|\?].*", plot_state_totals.plot_state_chart, name='plot_state_totals'),
    re_path(r"state_by_county_chart[\/|\?].*", plot_state_by_county.plot_state_by_county_chart, name='plot_state_by_county'),
    re_path(r"political_affiliation[\/|\?].*", political_affiliation.plot_affiliation, name='political_affiliation'),
    re_path(r"top_states[\/|\?].*", plot_top_states.plot_top_states, name='top_states'),
]
