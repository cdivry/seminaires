# ************************************************************************** #
#                                                                            #
#                                                        :::      ::::::::   #
#   urls.py                                            :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: Clement DIVRY <divry@ljll.math.upmc.fr>    +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2017/01/31 13:37:00 by divry              #+#    #+#            #
#   Updated: 2017/01/31 13:37:00 by divry             ###   ########.fr      #
#                                                                            #
# ************************************************************************** #

from django.conf.urls import url
from . import views
from .seminaires import ROUTE_ICS, ROUTE_JSON

urlpatterns = [
    url(r'^$', views.seminaires_index),
    url(r'^' + ROUTE_ICS  + '$', views.ics_directory_index),
    url(r'^' + ROUTE_ICS  + '(?P<fichier>.*).ics$',  views.ics_file),
    url(r'^' + ROUTE_JSON + '$', views.json_directory_index),
    url(r'^' + ROUTE_JSON + '(?P<fichier>.*).json$', views.json_file),
]
