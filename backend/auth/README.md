# Auth 

## Getting started

### Building and running for development

**Steps:**

0. Create `.env` file at the project's root directory and fill it with necessary environment variables.
You can find an example of `.env` file in `.env.example`.

1. Build and run docker container with `dev` env:

 ```commandline
./scripts/dev.sh up -d
 ```

2. Activate virtual environment:

 ```commandline
poetry shell
 ```

3. Run `auth` service locally:

```commandline
uvicorn src.main:app --reload
 ```

or

```commandline
python -m src.main
```

run tests
```commandline
pytest ./tests 
```


## Running database migrations

NOTE: First run your database inside of docker container

### Apply migrations
```
alembic upgrade head
```

### Create superuser via CLI

To create superuser with all service permissions granted:

```commandline
python -m src.cli.main create-superuser --username superadmin --first-name Jack --last-name Smith
```

or you can create it manually. Role name should be `superadmin`
