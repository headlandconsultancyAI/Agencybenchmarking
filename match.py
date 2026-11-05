"""Turns the term lists in topics.py into compiled regexes."""
import re

def _term(t):
    t = t.strip().lower()
    parts = []
    for word in t.split(" "):
        w = re.escape(word).replace(r"\*", r"[\w'\u2019-]*")
        parts.append(w)
    return r"\s+".join(parts)

def compile_terms(terms):
    alts = []
    for t in terms:
        for a in t.split("|"):
            # very short terms (ai, geo, nhs) don't match inside hyphenated words,
            # so "Geo-Commerce" isn't read as GEO
            tail = r"(?![\w]|-\w)" if len(a.strip()) <= 3 else r"(?![\w])"
            alts.append(_term(a) + tail)
    return re.compile(r"(?<![\w#@])(?:" + "|".join(alts) + r")", re.I)

def compile_model(model):
    return {k: compile_terms(v) for k, v in model.items()}

def tag(text, compiled):
    return [k for k, rx in compiled.items() if rx.search(text or "")]
