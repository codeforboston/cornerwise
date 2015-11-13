from collections import defaultdict
from math import log
import re, redis

def raw_frequencies(terms):
    freqs = defaultdict(int)
    for term in terms:
        freqs[term] += 1
    return freqs

def term_frequencies(raw_freq):
    max_freq = max(raw.values())

    return {term: (0.5*freq)/max_freq for term, freq in raw.items()}

def escape_term(term):
    return term.replace(" ", "_")\
               .replace(":", "")

def term_key(term):
    return "idf:words:" + escape_term(term)

def add_document(r, terms):
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

def inverse_frequency(r, term):
    doc_total = r.get("idf:doc_count")
    doc_word_total = r.get(term_key(term) + ":docs")

    return log(doc_total/doc_word_total)

def tfidf(r, term):
    pass
