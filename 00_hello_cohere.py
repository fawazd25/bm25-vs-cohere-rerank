import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.ClientV2()

query = "Combien de temps faut-il cuire des spaghettis ?"

docs = [
        "Les spaghettis sont apparus en Italie et on les cuisine aujourd’hui dans le monde entier.",
        "Faites cuire les pâtes environ dix minutes dans l’eau bouillante salée, puis égouttez-les.",
        "Un paquet de spaghettis se conserve plusieurs mois dans un placard sec, à l’abri de la lumière.",
        "Nombreux sont les enfants qui adorent faire du vélo.",
        "Pour une bonne sauce tomate, faites revenir l’ail dans l’huile d’olive avant d’ajouter les tomates.",
]

results = co.rerank(
    model="rerank-v5.0-pro", query=query, documents=docs, top_n = 5
)

for rang, r in enumerate(results.results, start =  1):
        print(f"{rang}. " + f" {round(r.relevance_score, 3)} " + f" {docs[r.index]} ")