=====
SEMINAIRES
=====

-----------

Une application Django/Wagtail qui genere les fichiers .ics (iCalendar) et .json pour permettre une collecte de flux par l'Agenda des Mathematiques. Les fichiers sont generes depuis les Evenements stockes en base grace au modele de page EventPage.

-----------

- Quick start

1. source bin/activate dans votre virtualenv django

2. pip install -r requirements.txt
   pip install django (if you dont already installed it in your env)

3. supprimez les fichiers dist de votre app avant sa regeneration
rm -fr seminaires/dist

4. supprimez egalement les eventuelles informations a propos de l'application precedemment generee
rm -fr seminaires/seminaires.egg-info

5. generez a nouveau l'application
python3 seminaires/setup.py sdist

6. deployez votre application grace a pip
pip install --upgrade seminaires/dist/seminaires-1337.tar.gz

7. ajoutez l'application dans votre settings.py
INSTALLED_APPS = [
	...
    'seminaires',
	...
]

8. ajoutez la route dans votre urls.py principal
    url(r'^ical/', include(seminaires.urls)),

9. integrez les modeles EventListing et EventPage dans vos modeles principaux Django (cf. models.py)
class EventListing(Page):
class EventPage(Page):

10. appliquez les migrations
./manage.py makemigrations
./manage.py migrate

11. redemarrez votre serveur django
./manage.py runserver

