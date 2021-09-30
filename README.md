# Androminacrew
This is a REST API that registers the time a User has worked in Task from a Company

## Development
### 1. Create a python3 env

    virtualenv -p python3 <env_name>

### 2. Install dependencices

    pip install -r requirements.txt

### 3. Install pre-commit github hook scripts

    pre-commit install

### 4. Create a postgres database

    createdb <db_name>

### 5. Set env variables
Create an .env file in the root directory. You can take .env_sample as an example

### 6. Run the application

    python manage.py runserver
