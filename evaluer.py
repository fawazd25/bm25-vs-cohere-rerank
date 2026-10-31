import json
from bm25 import rechercher

def charger_questions(chemin="questions.jsonl"):
    questions = []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                q = json.loads(ligne)
                questions.append(q)
    return questions


def rang_premier_pertinent(resultats, relevant):
    for rang, pid in enumerate(resultats, start=1):
        if pid in relevant:
            return rang
    return None


def evaluer(rechercher, questions):
    r5, r20, mrr = [], [], []

    for q in questions:
        resultats = rechercher(q["question"], 20)
        rang = rang_premier_pertinent(resultats, q["relevant"])

        print(q["id"], q["style"], rang)

        r5.append(1 if rang is not None and rang <= 5 else 0)
        r20.append(1 if rang is not None else 0)
        mrr.append((1 / rang) if rang is not None else 0)

    return sum(r5) / len(r5), sum(r20) / len(r20), sum(mrr) / len(mrr)


if __name__ == "__main__":
    questions = charger_questions()
    reglage = [q for q in questions if q["split"] == "reglage"]
    r5, r20, mrr = evaluer(rechercher, reglage)
    print(f"recall@5 = {r5:.3f}   recall@20 = {r20:.3f}   MRR@20 = {mrr:.3f}")
