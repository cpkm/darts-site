## Getting started
This web-app is written in Flask (Python 3), using SQLAlchemy for databasing and Bootstrap for HTML formatting. The easiest way to get up and running is to use a Python virutal environment. To load the virtual environment, for example using Anaconda, navigate in to the clone repo, then run:

```
conda env create -f darts-env.yml
```
Activate the environment using
```
conda activate darts-env
```

Alternatively, you may install all the required packages using the [requirements.txt](requirements.txt) file:
```
pip install -r requirements.txt
```

## Usage
Once the virtual environment is activated you can run the app locally.
```
flask run
```
The web address will be diplayed in the terminal window. If debugging is ON, output from the app will also be displayed in the terminal window. Use ctrl-c to stop the app.

A python shell which automatically loads important app files can be run using
```
flask shell
```
From here normal python cammands can by issued. Most app funcions and database classes are already imported and can be used immediately. E.g.
```python
Match.query.all()
```

## Updating the database
If the structure of the database is changed, i.e. changes to [models.py](app/models.py), it must be migrated and upgraded before use. To migrate run
```
flask db migrate -m "<insert breif description of changes>"
```
This will run a check of the code and list changes to the database. It will create a new migration file in [migrations/versions](migrations/versions). To upgrade to this newly created version, run
```
flask db upgrade
```
You can revert to previous migration versions using
```
flask db downgrade
```

## Updating evironment files
If new packages are installed, or there are other changes to the virtual environment, you must update the [darts-env.yml](darts-env.yml) and [requirements.txt](requirements.txt) files:
```
conda export darts-env.yml
pip freeze > requirements.txt
```
