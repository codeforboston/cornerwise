from collections import defaultdict
from math import log
from operator import itemgetter
import re


def raw_frequencies(terms):
    freqs = defaultdict(int)
    for term in terms:
        freqs[term] += 1
    return freqs


def term_frequencies(raw_freq):
    max_freq = max(raw_freq.values())

    return {term: (0.5*freq)/max_freq for term, freq in raw_freq.items()}


def escape_term(term):
    return term.replace(" ", "_")\
               .replace(":", "")\
               .lower()


def term_key(term):
    return "idf:words:" + escape_term(term)


def doc_key(doc_id):
    return "idf:docs:" + str(doc_id)


def add_document(r, terms, doc_id=None):
    if doc_id and not r.setnx(doc_key(doc_id), "true"):
        return

    terms = list(terms)

    # Increment the document count:
    r.incr("idf:doc_count")
    r.incr("idf:term_count", len(terms))

    raw_counts = raw_frequencies(terms)
    # Add the raw occurrence of each term:
    for term, count in raw_counts.items():
        r.incr(term_key(term) + ":raw", count)

    # And increment the document count for each unique term:
    for term in set(terms):
        r.incr(term_key(term) + ":docs")


def inverse_frequencies(r, terms):
    doc_total = r.get("idf:doc_count")

    return {term: log(doc_total/r.get(term_key(term) + ":docs"))
            for term in terms}


def tf_idf_terms(r, terms):
    tf = term_frequencies(raw_frequencies(terms))
    itf = inverse_frequencies(r, terms)

    return {term: tf[term] * itf[term] for ferm in terms}


def sorted_terms(r, terms):
    term_dict = tf_idf_terms(r, terms)

    return sorted(term_dict.items(), key=itemgetter(1), reverse=True)
