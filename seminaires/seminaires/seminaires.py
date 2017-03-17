#!/usr/bin/env python3
# ************************************************************************** #
#                                                                            #
#                                                        :::      ::::::::   #
#   seminaires.py                                      :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: Clement DIVRY <divry@ljll.math.upmc.fr>    +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2017/01/31 13:37:00 by divry              #+#    #+#            #
#   Updated: 2017/01/31 13:37:00 by divry             ###   ########.fr      #
#                                                                            #
# ************************************************************************** #

import datetime
import sqlite3
import time
import ast # str 2 dict
import json
import sys
from bs4 import BeautifulSoup
import time
from icalendar import Calendar, Event
from django.utils.feedgenerator import SyndicationFeed
from unidecode import unidecode

from .seminaires_config import \
    LABORATORY_NAME, \
    DB_PATH, \
    SITE_BASE_URL, \
    SITE_HOME_PATH, \
    ICS_PATH, \
    JSON_PATH, \
    ROUTE_ICS, \
    ROUTE_JSON

__all__ = (
    'Ics20Feed',
    'DefaultFeed',
)

FEED_FIELD_MAP = (
    ('product_id',          'prodid'),
    ('method',              'method'),
    ('title',               'x-wr-calname'),
    ('description',         'x-wr-caldesc'),
    ('timezone',            'x-wr-timezone'),
    ('ttl',                 'x-published-ttl'),
    # See format here: http://www.rfc-editor.org/rfc/rfc2445.txt (sec 4.3.6)
)

ITEM_EVENT_FIELD_MAP = (
    # PARAM              -> ICS FIELD
    ('unique_id',           'uid'),
    ('title',               'summary'),
    ('description',         'description'),
    ('start_datetime',      'dtstart'),
    ('end_datetime',        'dtend'),
    ('updateddate',         'last-modified'),
    ('created',             'created'),
    ('timestamp',           'dtstamp'),
    ('transparency',        'transp'),
    ('location',            'location'),
    ('geolocation',         'geo'),
    ('link',                'url'),
    ('organizer',           'organizer'),
    ('attendee',            'attendee'),
    ('status',              'status'),
    ('method',              'method'),
)


class Ics20Feed(SyndicationFeed):

    mime_type = 'text/calendar; charset=utf8'

    def write(self, outfile, encoding):
        cal = Calendar()
        cal.add('version', '2.0')
        cal.add('prodid', '-//SEMINAIRES/'+ LABORATORY_NAME + '/ICS v1.0//FR')
        cal.add('calscale', 'GREGORIAN')
        #cal.add('method', 'PUBLISH')
        for ifield, efield in FEED_FIELD_MAP:
            val = self.feed.get(ifield)
            if val is not None:
                cal.add(efield, val)
        self.write_items(cal)
        to_ical = getattr(cal, 'as_string', None)
        if not to_ical:
            to_ical = cal.to_ical
        outfile.write(to_ical())

    def write_items(self, calendar):
        for item in self.items:
            event = Event()
            for ifield, efield in ITEM_EVENT_FIELD_MAP:
                val = item.get(ifield)
                if val is not None:
                    event.add(efield, val)

            calendar.add_component(event)

DefaultFeed = Ics20Feed


def get_seminaires_identifier():
    identifier = 0
    query = "SELECT id FROM django_content_type WHERE model='eventlisting';"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for row in c.execute(query):
        identifier = int(row[0])
    if (identifier == 0):
        print("Veuillez appliquer la migration de votre modele EventListing.")
        sys.exit(0)
    return (str(identifier))

def get_seminaires_evenements_identifier():
    identifier = 0
    query = "SELECT id FROM django_content_type WHERE model='eventpage';"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for row in c.execute(query):
        identifier = int(row[0])
    if (identifier == 0):
        print("Veuillez appliquer la migration de votre modele EventPage.")
        sys.exit(0)
    return (str(identifier))

def get_seminaires(file_type=''):
    eventlist_identifier = get_seminaires_identifier()
    query = "SELECT id, url_path, title, slug FROM wagtailcore_page \
    WHERE content_type_id=" + eventlist_identifier + ";"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for each_list in c.execute(query):
        list_id = str(each_list[0])
        list_url = str(each_list[1])
        list_slug = str(each_list[3])
        list_title = str(each_list[2])
        get_seminaires_evenements(file_type, list_id, list_url, list_title, list_slug)

def get_seminaires_evenements_count(list_id, list_url):
    count = 0
    eventpage_identifier = get_seminaires_evenements_identifier()
    events = []
    query = "SELECT id, url_path \
             FROM wagtailcore_page \
             WHERE url_path like '" + list_url + "%' \
             AND id != " + list_id + " \
             AND content_type_id=" + eventpage_identifier + ";"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for row in c.execute(query):
        event_id = str(row[0])
        with sqlite3.connect(DB_PATH) as conn2:
            c2 = conn2.cursor()
            for eventpage in c2.execute("SELECT page_ptr_id \
                                         FROM core_eventpage \
                                         WHERE page_ptr_id=" + event_id + ";"):
                count += 1
    return (count)

def get_seminaires_evenements(file_type, list_id, list_url, list_title, list_slug):
    eventpage_identifier = get_seminaires_evenements_identifier()
    events = []
    query = "SELECT id, url_path \
             FROM wagtailcore_page \
             WHERE url_path like '" + list_url + "%' \
             AND id != " + list_id + " \
             AND content_type_id=" + eventpage_identifier + ";"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for row in c.execute(query):
        tmp = {}
        tmp['id'] = row[0]
        tmp['url'] = row[1]

        event_id = str(row[0])
        with sqlite3.connect(DB_PATH) as conn2:
            c2 = conn2.cursor()
            for eventpage in c2.execute("SELECT page_ptr_id, \
                                                date_start, \
                                                date_end, \
                                                organisateur, \
                                                intervenant, \
                                                interv_orga, \
                                                lieu,  \
                                                sujet, \
                                                body \
                                        FROM core_eventpage \
                                        WHERE page_ptr_id=" + event_id + ";"):

                tmp['uid'] = str(str(time.time()) + '' + str(eventpage[0]) + '@' + LABORATORY_NAME)
                tmp['stamp'] = eventpage[1]
                tmp['start'] = eventpage[1]
                tmp['end'] = eventpage[2]
                tmp['organizer'] = eventpage[3]
                tmp['intervenant'] = eventpage[4]
                tmp['orga_intervenant'] = eventpage[5]
                tmp['location'] = eventpage[6]
                tmp['titre'] = eventpage[7]
                tmp_desc = json.loads(str(eventpage[8]))
                try:
                    tmp['description'] = BeautifulSoup(str(tmp_desc[0]['value']), "html5lib")
                    tmp['description'] = tmp['description'].get_text()
                except:
                    tmp['description'] = ""
        events.append(tmp)
    query = "SELECT body FROM core_eventlisting WHERE page_ptr_id=" + list_id + ";"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    list_descr = ""
    for row in c.execute(query):
        try:
            list_descr = str(row[0])
            tmp_desc = json.loads(str(row[0]))[0]
            list_descr = BeautifulSoup(str(tmp_desc['value']), "html5lib")
            list_descr = list_descr.get_text()
        except:
            pass

    if file_type == 'ICS':
        ics_create(fichier=ICS_PATH + list_slug + '.ics',
                   title=str(list_title),
                   url=str(list_url),
                   desc=str(list_descr),
                   lang=u"fr",
                   events=events)
        print("ICS GENERATED : " + str(ICS_PATH + list_slug + '.ics'))
    elif file_type == 'JSON':
        json_create(fichier=JSON_PATH + list_slug + '.json',
                    sem_id=list_id,
                    title=str(list_title),
                    url=str(list_url),
                    desc=str(list_descr),
                    lang=u"fr",
                    events=events)
        print("JSON GENERATED : " + str(JSON_PATH + list_slug + '.json'))

def ics_create(fichier, title, url, desc, lang, events):
    feed = Ics20Feed(
        title=title,
        link=url,
        description=desc,
        language=lang,
    )
    for event in events:
        feed = ics_add_event(feed, event)
    fd = open(unidecode(fichier), 'wb')
    feed.write(fd, 'utf-8')
    fd.close()

def ics_add_event(feed, event):

    start = str(event['start']).split(' ')
    start = start[0].split('-') + start[1].split(':')
    start = datetime.datetime(int(start[0]), int(start[1]), int(start[2]), int(start[3]), int(start[4]))
    end = str(event['end']).split(' ')
    end = end[0].split('-') + end[1].split(':')
    end = datetime.datetime(int(end[0]), int(end[1]), int(end[2]), int(end[3]), int(end[4]))

    feed.add_item(
        unique_id=str(str(time.time()) + '-EVENT#' + str(event['id']) + '-@'+  LABORATORY_NAME),
        title=str(event['titre']),
        link=str(event['url']).replace(SITE_HOME_PATH, SITE_BASE_URL + '/'),
        description=str(event['description']),
        status=str('CONFIRMED'),
        location=str(event['location']),
        organizer=str(event['organizer']),
        attendee=str(event['intervenant']),
        timestamp=start,
        start_datetime=start,
        end_datetime=end,
    )
    return (feed)

def json_create(fichier, sem_id, title, url, desc, lang, events):
    feed = {}

    feed['count'] = get_seminaires_evenements_count(sem_id, url)
    feed['additionalInfo'] = {
        "path": {
            "url" : url.replace(SITE_HOME_PATH, SITE_BASE_URL + '/'),
            "name": title,
            "id"  : sem_id
        }
    }
    feed['results'] = []
    for event in events:
        feed['results'] = feed['results'] + [json_add_event(event)]
    try:
        tmp = bytes(json.dumps(feed, indent=4, sort_keys=False, ensure_ascii=False).encode('utf-8'), 'utf-8')
    except:
        tmp = bytes(unidecode(json.dumps(feed, indent=4, sort_keys=False, ensure_ascii=False)), 'latin1')
    fd = open(unidecode(fichier), 'wb')
    fd.write(tmp)
    fd.close()

def json_add_event(event):
    new_event = {
        "id"        : event['id'],
        "startDate" : {
            "date": event['start'].split(' ')[0].replace('-', ''),
            "time": event['start'].split(' ')[1],
            "tz": "Europe/Paris"
        },
        "endDate" : {
            "date": event['end'].split(' ')[0].replace('-', ''),
            "time": event['end'].split(' ')[1],
            "tz": "Europe/Paris"
        },
        "description": str(event['description']),
        "chairs":
        {
            "id": 1,
            "fullName": event['intervenant'],
            "affiliation": event['orga_intervenant']
        },
        "url": event['url'].replace(SITE_HOME_PATH, SITE_BASE_URL + '/'),
        "location": event['location'],
        "timezone": "Europe/Paris"
    }
    return (new_event)

def update_ics():
    # preserve les fichiers non-regeneres
    get_seminaires(file_type='ICS')

def update_json():
    # preserve les fichiers non-regeneres
    get_seminaires(file_type='JSON')

if __name__ == '__main__':

    get_seminaires(file_type='ICS')
    get_seminaires(file_type='JSON')
