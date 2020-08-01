# marks-covid-tracker
Django-based Covid Tracker based on Bokeh Visualizations

This application is based on publically available data from the Johns Hopkins University Center for Systems Science in Engineering.
"Dong E, Du H, Gardner L. An interactive web-based dashboard to track COVID-19 in real time. Lancet Inf Dis. 20(5):533-534. doi: 10.1016/S1473-3099(20)30120-1"

The application uses a Django web server to present various Bokeh visualizations of infection and death rates in the US by state, county and political affiliation. 

To add new visualization:
1. Create bokeh visualization with a function accepts a request which has named variables their default values for the chart.
- the code should be placed in the 'views' directory
- The signature's first variable must be a request.  plot_mychart(request, color='red', animal='frog')
- Return a django.JsonResponse(bokeh.json_item(p)), where 'p' is a bokeh plot.
- handle the request object to get variables passed

2. Create javascript function to add control elements.

3. Update the javascript to make_chart() on the DomLoaded function.

4. Update the urls.py