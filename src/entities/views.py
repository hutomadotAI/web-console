import logging
import urllib

from django.shortcuts import render|
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, View

from entities.services import get_entities, get_entity, save_entity
from entities.forms import *

logger = logging.getLogger(__name__)


