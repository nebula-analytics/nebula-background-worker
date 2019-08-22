Project Nebula Analytics/Oauth Demo
========

Setup
-----
Ensure you have python 3.7+ installed.

Install required libs:
`pip install -r requirements.txt`.

Use another application to generate a pickled oauth credential
such as https://github.com/nebula-analytics/nebula-ganalytics-poc

Run
-----
In terminal navigate to the directory of main.py.

1. Running `python main.py` or `python main.py --help` 
should display a guide to the arguments

2. To view a list of available accounts run the command 
`python main.py '<path_to_pickled_credentials>'` 

3. To start the background worker you will need to specify 
the analytics view to target as follows.
`python main.py '<path_to_pickled_credentials>' --view_id '<analytics_view_id>'`
    