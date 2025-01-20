bable-extract-messages:
	pybabel extract -o locales/messages.pot apps/bot core -k _ -k __

bable-init-language-en:
	pybabel init -i locales/messages.pot -d locales -D messages -l en

bable-init-language-ru:
	pybabel init -i locales/messages.pot -d locales -D messages -l ru

bable-init-language-uz:
	pybabel init -i locales/messages.pot -d locales -D messages -l uz

bable-compile:
	pybabel compile -d locales -D messages

bable-update:
	pybabel update -d locales -D messages -i locales/messages.pot

run-bot:
	python manage.py runbot