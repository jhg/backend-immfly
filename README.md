# Django Content Management System Backend

Content management system.

## About It

- Manage channels and sub-channels
- Manage content and associated files
- Calculate ratings for channels and contents
- Handle image uploads for channels and files for contents
- Signal-based cache invalidation and other optimizations
- Type annotations to pass strict Mypy checks.

## Requirements

- Python 3.11, 3.12, or 3.13
- Other dependencies listed in `requirements.txt`

## Usage

To try it in local:

```sh
git clone https://github.com/jhg/backend-immfly
cd backend-immfly
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

It's using SQLite for simple local development, but with Django
 any database could be used in production.

## Running Tests

```sh
coverage run manage.py test
coverage report

mypy . --strict
```

Or only `python manage.py test` if you don't want to check coverage
 and type annotations.
