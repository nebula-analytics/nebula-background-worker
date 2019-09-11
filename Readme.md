Project Nebula Analytics/Oauth Demo
========

Development Setup
-----
Ensure you have python 3.7+ installed.

####Dependencies:
In order to run the worker, you will need to install the following.
- Python (Version > 3.7)
- RabbitMQ
- MongoDB
- Redis (Optional for debugging)

###### Linux (Ubuntu)
`sudo apt update && sudo apt-get install rabbitmq mogodb redis python3`


TODO: Add instructions for running each application
###### MacOS
`brew install rabbitmq mogodb redis`

TODO: Add instructions for running each application

#### Installing Python Libraries

Install python dependencies:
`pip3 install -r requirements.txt`.

#### Configure the worker (TODO: Automate)
Add the required fields listed below to config.yaml

- analytics:
    - path_to_credentials:
        - Use another application to generate a pickled oauth credential such as https://github.com/nebula-analytics/nebula-ganalytics-poc
    - view_id:
        - Locate the id of the analytics view you want to target
        
        
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
    