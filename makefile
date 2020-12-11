ENV = django/penguin/.env
ENVP = .env_postgres
DC = docker-compose -f docker-compose.dev.yml
LHOME = python manage.py loaddata home/fixtures/data.json
LTHEME = python manage.py loaddata theme/fixtures/data.json

init:			${ENV} ${ENVP}

${ENV}:;		cp setup/.sample.env django/penguin/.env

${ENVP}:;		cp setup/.sample.env_postgres .env_postgres

install:        django/Pipfile.lock
				cd django && pipenv install --dev && cd ..

start:;			${DC} up --build

stop:;			${DC} down

loaddata:;		${DC} exec django sh -c  "${LHOME} && ${LTHEME}"
