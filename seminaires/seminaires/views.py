#-*-coding: utf-8-*-

# ************************************************************************** #
#                                                                            #
#                                                        :::      ::::::::   #
#   views.py                                           :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: Clement DIVRY <divry@ljll.math.upmc.fr>    +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2017/01/31 13:37:00 by divry              #+#    #+#            #
#   Updated: 2017/01/31 13:37:00 by divry             ###   ########.fr      #
#                                                                            #
# ************************************************************************** #

from __future__ import unicode_literals

from django.conf import settings
import mimetypes
import os
import posixpath
import re
import stat
from .seminaires import update_ics, update_json
from .seminaires import ICS_PATH, JSON_PATH, SITE_BASE_URL
from .seminaires import ROUTE_ICS, ROUTE_JSON

from django.http import (
    FileResponse, Http404, HttpResponse, HttpResponseNotModified,
    HttpResponseRedirect,
)
from django.template import Context, Engine, TemplateDoesNotExist, loader
from django.utils.http import http_date, parse_http_date
from django.utils.six.moves.urllib.parse import unquote
from django.utils.translation import ugettext as _, ugettext_lazy


##########################################
#         index de l'application         #
##########################################

def seminaires_index(request):
    template = ""
    try:
        with open(settings.BASE_DIR + '/seminaires/templates/seminaires/seminaires.html', 'rb') as fd:
            template = fd.read()
    except:
        raise ValueError("template 'seminaires.html' does not exists or cannot be read correctly.")
    t = Engine(libraries={'i18n': 'django.templatetags.i18n'}).from_string(template)
    c = Context({
        'path_ics': ROUTE_ICS,
        'path_json': ROUTE_JSON,
    })
    return HttpResponse(t.render(c))


##########################################
#       indexation des repertoires       #
##########################################

def ics_directory_index(name=''):
    update_ics()
    template = ""
    try:
        with open(settings.BASE_DIR + '/seminaires/templates/seminaires/repertoire.html', 'rb') as fd:
            template = fd.read()
    except:
        raise ValueError("template 'repertoire.html' does not exists or cannot be read correctly.")
    t = Engine(libraries={'i18n': 'django.templatetags.i18n'}).from_string(template)
    files = []
    for f in os.listdir(ICS_PATH):
        maybe_dir = os.path.join(ICS_PATH + '/', f)
        if not os.path.isdir(maybe_dir) and not f.startswith('.') and f.endswith('.ics'):
            if os.path.isdir(os.path.join(ICS_PATH, f)):
                f += '/'
            files.append(f)
    c = Context({
        'directory': ROUTE_ICS,
        'url':       SITE_BASE_URL + '/seminaires/' + ROUTE_ICS,
        'file_list': files,
    })
    return HttpResponse(t.render(c))


def json_directory_index(name=''):
    update_json()
    template = ""
    try:
        with open(settings.BASE_DIR + '/seminaires/templates/seminaires/repertoire.html', 'rb') as fd:
            template = fd.read()
    except:
        raise ValueError("template 'repertoire.html' does not exists or cannot be read correctly.")
    t = Engine(libraries={'i18n': 'django.templatetags.i18n'}).from_string(template)
    files = []
    for f in os.listdir(JSON_PATH):
        maybe_dir = os.path.join(JSON_PATH + '/', f)
        if not os.path.isdir(maybe_dir) and not f.startswith('.') and f.endswith('.json'):
            if os.path.isdir(os.path.join(JSON_PATH, f)):
                f += '/'
            files.append(f)
    c = Context({
        'directory': ROUTE_JSON,
        'url':       SITE_BASE_URL + '/seminaires/' + ROUTE_JSON,
        'file_list': files,
    })
    return HttpResponse(t.render(c))


##########################################
#            servir un fichier           #
##########################################

def ics_file(request, fichier):
    update_ics()
    contenu = ""
    try:
        with open(ICS_PATH + fichier + '.ics', 'rb') as fd:
            contenu = fd.read()
    except:
        raise Http404
    response = HttpResponse(contenu, content_type="text/calendar")
    return (response)


def json_file(request, fichier):
    update_json()
    contenu = ""
    try:
        with open(JSON_PATH + fichier + '.json', 'rb') as fd:
            contenu = fd.read()
    except:
        raise Http404
    response = HttpResponse(contenu, content_type="application/json")
    return (response)

