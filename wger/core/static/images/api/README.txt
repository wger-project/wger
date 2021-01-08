pip3 install django-extensions
apt install python3-pygraphviz

./manage.py graph_models --theme django2018 --pygraphviz -g -o wger/core/static/images/api/db-all.svg config core exercises gym mailer manager nutrition weight
./manage.py graph_models --theme django2018 --pygraphviz -g -o wger/core/static/images/api/db-exercises.svg exercises
./manage.py graph_models --theme django2018 --pygraphviz -g -o wger/core/static/images/api/db-manager.svg manager
./manage.py graph_models --theme django2018 --pygraphviz -g -o wger/core/static/images/api/db-nutrition.svg config nutrition
