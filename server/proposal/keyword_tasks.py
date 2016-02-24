import datetime
import logging
import redis
from django.conf import settings

from cornerwise import celery_app

from scripts import idf, keywords
from scripts.text_analytics import TextAnalyzer
from .models import Attribute


logger = logging.getLogger(__name__)

if hasattr(settings, "AZURE_API_KEY"):
    text_analyzer = TextAnalyzer(settings.AZURE_API_KEY)
else:
    logger.warning("You must set AZURE_API_KEY in local_settings.py " +
                   "to use the text analyzer")


# For testing:
def add_full_text(r, doc):
    ""
    terms = keywords.keywords(doc.get_text())
    idf.add_document(r, terms, doc.pk)


def add_full_docs(docs):
    r = redis.StrictRedis()
    pipe = r.pipeline(transaction=False)

    for doc in docs:
        key = "keywords:" + doc.pk + ":added"
        if r.get(key):
            continue
        if doc.fulltext:
            add_full_text(r, doc)
            pipe.set(key, datetime.now().stamp())

    pipe.execute()


def top_terms(doc):
    r = redis.StrictRedis()
    try:
        terms = text_analyzer.get_key_phrases(doc.get_text())
    except:
        return []
    sorted_terms = idf.sorted_terms(r, terms)
    return [t[0] for t in sorted_terms]


celery_app.task(name="proposal.build_counts")
def build_counts(handles=[]):
    attrs = Attribute.objects.filter(handle__in=handles)
    r = redis.StrictRedis()

    for att in attrs:
        try:
            att_keywords = text_analyzer.get_key_phrases(att.text_value)
        except:
            continue
        idf.add_document(r, att_keywords, att.pk)


celery_app.task(name="proposal.analyze_text")
def analyze_document_text(doc):
    att_keywords = keywords.keywords(doc.get_text())
