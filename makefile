all:			program

program:		django/penguin/.env postgres/.env_postgres
				cp setup/.sample.env django/penguin/.env && cp setup/.sample.env_postgres postgres/.env_postgres

install:        django/Pipfile.lock
				cd django && pipenv install --dev && cd ..

start:;			docker-compose -f docker-compose.dev.yml up --build

loaddata:;		docker-compose -f docker-compose.dev.yml exec django python manage.py loaddata home/fixtures/data.json
