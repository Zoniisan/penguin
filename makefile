all:			program

program:		django/penguin/.env .env_postgres
				cp setup/.sample.env django/penguin/.env && cp setup/.sample.env_postgres .env_postgres

install:        django/Pipfile.lock
				cd django && pipenv install --dev && cd ..

start:;			docker-compose -f docker-compose.dev.yml up --build

stop:;			docker-compose -f docker-compose.dev.yml down

loaddata:;		docker-compose -f docker-compose.dev.yml exec django python manage.py loaddata home/fixtures/data.json
