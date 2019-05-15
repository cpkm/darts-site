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
