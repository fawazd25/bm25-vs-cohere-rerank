import json
import time
from pathlib import Path
import cohere
from dotenv import load_dotenv
from bm25 import rechercher as rechercher_bm25

load_dotenv()
co = cohere.ClientV2()
CHEMIN_CACHE = Path("cache") / "rerank.json"

def charger_textes(chemin="corpus.jsonl"):
    textes = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                p = json.loads(ligne)
                textes[p["id"]] = p["text"]
    return textes


TEXTES = charger_textes()


def charger_cache():
    if CHEMIN_CACHE.exists():
        return json.loads(CHEMIN_CACHE.read_text(encoding="utf-8"))
    return {}


def sauver_cache(cache):
    CHEMIN_CACHE.parent.mkdir(exist_ok=True)
    CHEMIN_CACHE.write_bytes(json.dumps(cache, ensure_ascii=False, indent=2).encode("utf-8"))

CACHE = charger_cache()


def rechercher(question, k=20):
    candidats = rechercher_bm25(question, 20)

    if question in CACHE:
        print("cache")
        classement = CACHE[question]["classement"]
    else:
        print("appel API")
        debut = time.perf_counter()
        reponse = co.rerank(
            model="rerank-v5.0-pro",
            query=question,
            documents=[TEXTES[i] for i in candidats],
            top_n=20,
        )
        duree = time.perf_counter() - debut

        classement = [candidats[r.index] for r in reponse.results]
        CACHE[question] = {
            "candidats": candidats,
            "classement": classement,
            "scores": [r.relevance_score for r in reponse.results],
            "duree_s": round(duree, 3),
        }
        sauver_cache(CACHE)
        time.sleep(7)

    return classement[:k]


if __name__ == "__main__":
    q15 = "Comment un attaquant peut-il rendre un assistant documentaire incapable de répondre à une question précise ?"
    print(rechercher(q15, 5))