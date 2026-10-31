import re
import json
from rank_bm25 import BM25Okapi

# Essai unique sur le réglage : retirer les mots vides français.
# Liste fixée avant de voir les résultats. Résultat : MRR@20 0,612 -> 0,643,
# mais recall@20 1,0 -> 0,8 (q13 et q15 sortent du top 20). Non retenu.
MOTS_VIDES = set("""
le la les l un une des du de d et ou en à au aux ce ces cet cette
qu que qui quoi quel quelle quels quelles est sont être a ont
il elle ils elles on se s son sa ses leur leurs par pour sur dans
avec sans ne pas plus y t n c j m
""".split())

RETIRER_MOTS_VIDES = True


def tokeniser(texte):
    mots = re.findall(r"\w+", texte.lower())
    if RETIRER_MOTS_VIDES:
        mots = [mot for mot in mots if mot not in MOTS_VIDES]
    return mots


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
