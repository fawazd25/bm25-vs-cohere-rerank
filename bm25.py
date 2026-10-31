import re
import json
from rank_bm25 import BM25Okapi


def tokeniser(texte):
    return re.findall(r"\w+", texte.lower())


def charger_corpus(chemin="corpus.jsonl"):
    ids = []
    textes_tokenises = []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                p = json.loads(ligne)
                ids.append(p["id"])
                textes_tokenises.append(tokeniser(p["text"]))
    return ids, textes_tokenises


IDS, TEXTES = charger_corpus()
BM25 = BM25Okapi(TEXTES)


def rechercher(question, k=20):
    scores = BM25.get_scores(tokeniser(question))
    ordre = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [IDS[i] for i in ordre[:k]]


if __name__ == "__main__":
    print(rechercher("Qu'est-ce que la règle des deux pour sécuriser un agent d'IA ?", 5))