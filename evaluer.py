import json
import sys
import bm25
import rerank
from datetime import date
from pathlib import Path


METHODES = {"bm25": bm25.rechercher, "rerank": rerank.rechercher}


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


def evaluer_detail(rechercher, questions):
    """Une ligne par question : son id, son style, le rang obtenu et les 5 premiers résultats."""
    details = []
    for q in questions:
        resultats = rechercher(q["question"], 20)
        rang = rang_premier_pertinent(resultats, q["relevant"])
        print(q["id"], q["style"], rang)
        details.append({"id": q["id"], "style": q["style"], "rang": rang, "top5": resultats[:5]})
    return details


def moyennes(details):
    rangs = [d["rang"] for d in details]
    r5 = [1 if rang is not None and rang <= 5 else 0 for rang in rangs]
    r20 = [1 if rang is not None else 0 for rang in rangs]
    mrr = [(1 / rang) if rang is not None else 0 for rang in rangs]
    return sum(r5) / len(r5), sum(r20) / len(r20), sum(mrr) / len(mrr)


def evaluer(rechercher, questions):
    return moyennes(evaluer_detail(rechercher, questions))


def afficher(nom, r5, r20, mrr):
    print(f"{nom:12} recall@5 = {r5:.3f}   recall@20 = {r20:.3f}   MRR@20 = {mrr:.3f}")


def evaluer_test(rechercher, questions, methode):
    """Évaluation finale sur le test : une seule fois, résultat enregistré dans resultats/."""
    sortie = Path("resultats") / f"{methode}_test.json"
    if sortie.exists():
        sys.exit(f"{sortie} existe déjà : le test a déjà été lancé pour {methode}. Rien n'a été relancé.")

    test = [q for q in questions if q["split"] == "test"]
    details = evaluer_detail(rechercher, test)

    resultat = {"methode": methode, "split": "test", "date": date.today().isoformat(), "n": len(test)}
    r5, r20, mrr = moyennes(details)
    resultat["global"] = {"recall@5": r5, "recall@20": r20, "mrr@20": mrr}
    afficher("global", r5, r20, mrr)
    resultat["par_style"] = {}
    for style in ("litteral", "reformule"):
        groupe = [d for d in details if d["style"] == style]
        r5, r20, mrr = moyennes(groupe)
        resultat["par_style"][style] = {"n": len(groupe), "recall@5": r5, "recall@20": r20, "mrr@20": mrr}
        afficher(f"{style} ({len(groupe)})", r5, r20, mrr)
    resultat["questions"] = details

    sortie.parent.mkdir(exist_ok=True)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Résultats enregistrés dans {sortie}")


if __name__ == "__main__":
        # python evaluer.py réglage, BM25
        # python evaluer.py rerank réglage, BM25 + Rerank
        # python evaluer.py test  test, BM25 (une seule fois)
        # python evaluer.py test rerank test, BM25 + Rerank (une seule fois)
        args = sys.argv[1:]
        methode = "rerank" if "rerank" in args else "bm25"
        rechercher = METHODES[methode]
        questions = charger_questions()

        if "test" in args:
            evaluer_test(rechercher, questions, methode)
        else:
            reglage = [q for q in questions if q["split"] == "reglage"]
            afficher(f"{methode}", *evaluer(rechercher, reglage))
