#-*-coding: utf-8-*-

from django.shortcuts import render, redirect
from django.db.models import DateField, BooleanField, DateTimeField
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailadmin.widgets import AdminDateTimeInput
import wagtail.wagtaildocs
import datetime
import json
import locale
import os



# modele contenant une liste d'evenements

class EventListing(Page):

    class Meta:
        verbose_name = "Groupe d'évènements"


    type_evenement = models.CharField(
        choices=[
            ('gt', 'Groupe de travail'),
            ('seminaire', 'Séminaire'),
            ('theses', 'Soutenances de thèse')
        ],
        verbose_name="Type d'évènement",
        default="seminaire",
        max_length=1024,
        help_text="Type des évènements qui seront contenus dans cette liste"
    )

    body = StreamField([
        ('titre', blocks.CharBlock(classname="full title")),
        ('texte', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('lien', blocks.URLBlock()),
        ('html', blocks.RawHTMLBlock())
    ])

    def serve(self, request):
        if "format" in request.GET:
            if request.GET['format'] == 'json':
                children = EventPage.objects.live().descendant_of(self)
                events = []
                for e in children:
                    event = {}
                    event['id'] = e.id
                    event['start'] = int(e.date_start.timestamp() * 1000)
                    event['end'] = int(e.date_end.timestamp() * 1000)
                    event['title'] = e.title
                    event['url'] = e.url
                    event['class'] = 'event-info'
                    events.append(event)
                response = HttpResponse(
                    json.dumps(events),
                    content_type='application/json',
                )
                response['Content-Disposition'] = 'attachment; filename=' + self.slug + '.json'
                return response
            else:
                message = 'Could not export event\n\nUnrecognised format: ' + request.GET['format']
                return HttpResponse(message, content_type='text/plain')
        else:
            children = EventPage.objects.live().descendant_of(self)
            events = []
            for e in children:
                event = {}
                event['id'] = e.id
                event['start'] = e.date_start
                event['end'] = e.date_end
                event['title'] = e.title
                event['url'] = e.url
                events.append(event)
            return render(request, "templates/event_listing.html", {'self':self, 'events': events})

EventListing.content_panels = [
    FieldPanel('title'),
    FieldPanel('type_evenement'),
    StreamFieldPanel('body'),
]


# modele d'un evenement

class EventPage(Page):
    class Meta:
        verbose_name = "Evènement"

    @property
    def tiny_datestring(self):
        """
        Returns a representation of the event's datetimes suited for the homepage.
        """
        if not hasattr(self, '_datestring'):
            day_start = self.date_start.date()
            day_end = self.date_end.date()
            h_start = self.date_start.time()
            h_end = self.date_end.time()
            locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
            if day_start == day_end:
                self._datestring = "{}, {} - {}".format(day_start.strftime("%d/%B/%Y"),
                                                       h_start.strftime("%H:%M"),
                                                       h_end.strftime("%H:%M")
                                                       ).lower()
            else:
                self._datestring = "{}, {} - {}, {}".format(day_start.strftime("%d/%m/%Y"),
                                                            h_start.strftime("%H:%M"),
                                                            day_end.strftime("%d/%m/%Y"),
                                                            h_end.strftime("%H:%M")
                                                            ).lower()
        return self._datestring


    date_start = DateTimeField('Date de début')
    date_end = DateTimeField('Date de fin')
    all_day = BooleanField("Toute la journée", default=False)
    organisateur =  models.CharField(verbose_name="Organisateur", max_length=64)
    intervenant =  models.CharField(verbose_name="Intervenant", max_length=64)
    interv_orga =  models.CharField(verbose_name="Organisme de l'intervenant", max_length=128)
    lieu =  models.CharField(verbose_name="Lieu", max_length=256)
    sujet =  models.CharField(verbose_name="Sujet", max_length=256)


    body = StreamField([
        ('titre', blocks.CharBlock(classname="full title")),
        ('texte', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('lien', blocks.URLBlock()),
        ('html', blocks.RawHTMLBlock())
    ])

    def serve(self, request, *args, **kwargs):
        day_start = self.date_start.date()
        day_end = self.date_end.date()
        h_start = self.date_start.time()
        h_end = self.date_end.time()
        locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
        if day_start == day_end:
            datestring = "Le {} de {} à {}".format(day_start.strftime("%A %d %B %Y"),
                                                   h_start.strftime("%Hh%M"),
                                                   h_end.strftime("%Hh%M")
                                                   ).lower()
        else:
            datestring = "Du {} à {} au {} à {}".format(day_start.strftime("%A %d %B %Y"),
                                                        h_start.strftime("%Hh%M"),
                                                        day_end.strftime("%A %d %B %Y"),
                                                        h_end.strftime("%Hh%M")
                                                        ).lower()
        return render(request, "templates/event_page.html", {'self':self,
                                                        'datestring': datestring})


EventPage.content_panels = [
    FieldPanel('title'),
    FieldPanel('all_day'),
    FieldPanel('date_start', widget=AdminDateTimeInput(format='%d/%m/%Y %H:%M')),
    FieldPanel('date_end', widget=AdminDateTimeInput(format='%d/%m/%Y %H:%M')),
    FieldPanel('organisateur'),
    FieldPanel('intervenant'),
    FieldPanel('interv_orga'),
    FieldPanel('lieu'),
    FieldPanel('sujet'),
    StreamFieldPanel('body'),
]
