"""Sector classifier: Multinomial Naive Bayes written from scratch (no ML libraries).
Labels come from the CPV code on real notices; the model then predicts a sector for notices without one."""
import math
import re
from collections import Counter, defaultdict

_CPV = {"45": "Construction", "44": "Construction", "43": "Construction", "71": "Engineering", "72": "IT & Software",
        "48": "IT & Software", "30": "IT & Software", "32": "IT & Software", "33": "Healthcare", "85": "Healthcare",
        "09": "Energy", "65": "Energy", "31": "Energy", "60": "Transport", "34": "Transport", "63": "Transport",
        "90": "Environment", "77": "Environment", "79": "Business Services", "66": "Business Services",
        "73": "Business Services", "80": "Education", "15": "Food & Hospitality", "55": "Food & Hospitality",
        "50": "Maintenance"}
_STOP = set("and the for of in to with from services service supply provision tender framework agreement".split())


def cpv_sector(cpv):
    if not cpv or len(cpv) < 2:
        return None
    return _CPV.get(cpv[:2], "Other")


def toks(t):
    return [w for w in re.findall(r"[a-z]{3,}", t.lower()) if w not in _STOP]


class NaiveBayes:
    def fit(self, texts, labels):
        self.prior, self.cnt, self.tot = Counter(labels), defaultdict(Counter), Counter()
        self.vocab = set()
        for t, y in zip(texts, labels):
            for w in toks(t):
                self.cnt[y][w] += 1
                self.tot[y] += 1
                self.vocab.add(w)
        self.n = len(labels)
        return self

    def predict(self, text):
        ws, best, best_s = toks(text), None, -1e18
        for y, c in self.prior.items():
            s = math.log(c / self.n)
            for w in ws:
                s += math.log((self.cnt[y][w] + 1) / (self.tot[y] + len(self.vocab) + 1))
            if s > best_s:
                best, best_s = y, s
        return best


def evaluate(rows):
    """Deterministic 80/20 split. rows = [(title, sector)]. Accuracy vs. a majority-class baseline."""
    train = [r for i, r in enumerate(rows) if i % 5]
    test = [r for i, r in enumerate(rows) if i % 5 == 0]
    nb = NaiveBayes().fit([t for t, _ in train], [y for _, y in train])
    acc = sum(nb.predict(t) == y for t, y in test) / max(len(test), 1)
    majority = Counter(y for _, y in train).most_common(1)[0][0]
    base = sum(y == majority for _, y in test) / max(len(test), 1)
    return {"train": len(train), "test": len(test), "accuracy": acc, "baseline": base}
