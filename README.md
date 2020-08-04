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


Serving Static Files
(https://dev.to/learndjango/django-static-files-tutorial-1fg7)
For production, static files are centrally collectef using `python manage.py collectstatic`.  This will store the static files into a directory identified in settings as 'STATIC_ROOT'.  We then use Whitenoise to serve the static files in production.

This configuration requires several new variables in the settings.py confuration under the static files section.

Important: changes to static files under the app directory will require you to run `python manage.py collectstatic` to update the centrally managed static files.

This will allow the application to run using a wsgi configuration for production.

`gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 600 tracker.wsgi`

DOCKER
The docker image can be built using:
`docker build . -t covid_tracker`

A container from this image can be started via:
`docker run --rm --env-file ./.env -it -p 8080:8000 covid_tracker` 

AZURE
`az acr build --image covid_tracker --registry mcdomx --file Dockerfile .`
