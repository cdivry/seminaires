# SEMINAIRES

Une application Django/Wagtail (python3) qui genere les fichiers .ics (iCalendar) pour permettre une collecte de flux par l'Agenda des Mathematiques ( https://portail.math.cnrs.fr/agenda ).

Les fichiers sont generes depuis les Evenements stockes en base grace au modele de page EventPage.

-----------

### Quick start

- `source bin/activate` dans votre virtualenv django

- `pip install -r requirements.txt`

   `pip install django` (if you dont already installed it in your env)

- supprimez les fichiers dist de votre app avant sa regeneration

`rm -fr seminaires/dist`

- supprimez egalement les eventuelles informations a propos de l'application precedemment generee

`rm -fr seminaires/seminaires.egg-info`

- generez a nouveau l'application

`python3 seminaires/setup.py sdist`

- deployez votre application grace a pip

`pip install --upgrade seminaires/dist/seminaires-1337.tar.gz`

- ajoutez l'application dans votre settings.py
```
INSTALLED_APPS = [
	...
    'seminaires',
	...
]
```

- ajoutez la route dans votre urls.py principal
```
    url(r'^ical/', include(seminaires.urls)),

```

- integrez les modeles EventListing et EventPage dans vos modeles principaux Django (cf. models.py)
```
class EventListing(Page):
class EventPage(Page):
```

- appliquez les migrations
```
./manage.py makemigrations
./manage.py migrate
```

- redemarrez votre serveur django
```
./manage.py runserver
```
