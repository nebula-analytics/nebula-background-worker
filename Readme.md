Project Nebula Analytics / Background Worker
========

Installation
-----
Ensure you have python 3.7+ installed.

```brew install python ```

Finally, you will need to install mongodb for use as a data store.

```brew install mongodb```

Additionally, you will need to install a message queue client, rabbitmq is recommended.

```brew install rabbitmq```

Setup
-----

Install python dependencies:
`pip install -r requirements.txt`.


such as https://github.com/nebula-analytics/nebula-ganalytics-poc

In the [config.yaml](config.yaml) fill out the following fields:
```yaml
analytics:
  path_to_credentials: Use another application to generate a pickled oauth credential, put the path to the credentials in this field
  view_id: This should be set to the valid view id for the account referenced in the above credentials
primo:
  host: This value should be set to a valid promo host ending in /pnxs, see https://developers.exlibrisgroup.com/primo/apis/webservices/rest/pnxs/
```

You may need to modify other options in the model.config if you are operating 
in an environment with credentials. **TODO: Document config options**

Deployment
----------

#### Development Environment

##### Mac OS & Linux

You can run the scheduler, and a single worker for both queues application with the following command

```
python -m celery -A schedule worker -B --loglevel=debug -c=2 -Q nebula.express,nebula.import
```

##### Windows

On windows, the -B development option is not available, you can run a worker node using the following command.
```
python -m celery -A schedule worker --loglevel=debug -c=2 -Q nebula.express,nebula.import
```

With the worker node added, you can start the scheduler with the command below.
```
python -m celery -A schedule beat --loglevel=debug
```

#### Production Environment

A Production deployment process is being developed, in the mean time
the recommended deployment process is as follows

```
# Purge the queue of stale events
celery -A schedule purge -Q nebula.express,nebula.import

# Start the import queue.
python -m celery -A schedule worker --loglevel=debug -c=2 -Q nebula.import

# Start the short sync event queue 
python -m celery -A schedule worker --loglevel=debug -c=2 -Q nebula.express

# Start the scheduler
python -m celery -A schedule beat --loglevel=debug
```

