"""Symptom controller module"""

from tg import expose, request, abort, redirect, predicates
from xml.etree import ElementTree as ET
import uuid

from blockpca.lib.base import BaseCtller
from blockpca.model import DBSession, User, PrivateKey
from blockpca.lib.renderpr import match_field
from blockpca.lib.records import retrieve_record, store_record


__all__ = ['SymptomController']


class SymptomController(BaseCtller):
    allow_only = predicates.not_anonymous()

    @expose('blockpca.templates.symptoms')
    def index(self):
        return dict()

    @expose('blockpca.templates.diagnosis')
    def diagnosis(self):
        print('ohea')
        return dict()
