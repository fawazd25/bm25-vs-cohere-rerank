import json
import random

def split():
    questions = []
    with open("questions.jsonl", encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                q = json.loads(ligne)
                questions.append(q)

    random.Random(42).shuffle(questions)

    for i, q in enumerate(questions):
        if i < 10 :
            q["split"] = "reglage"
        else :
            q["split"] = "test"

    with open("questions.jsonl", "w",encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    split()