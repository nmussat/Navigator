# Navigator

A Postgresql database navigator exposing a REST API and a HTML interface to query database schema and statistics.

## Run

```bash
mkvirtualenv navigator
pip install -r requirements.txt
touch settings_dev.py
APP_SETTINGS=settings_dev.py python run.py

curl -H 'Content-Type: application/json' http://localhost:5000/schemas
```

Requires edge versions of both Flask and Flask-SQLAlchemy.
