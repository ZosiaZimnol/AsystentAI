import sys
import json
import requests
from textwrap import shorten

# ====================================
# KONFIGURACJA
# ====================================
EMBEDDINGS_URL = "http://localhost:8085/v1/embeddings"
WEAVIATE_GRAPHQL_URL = "http://localhost:8080/v1/graphql"
OLLAMA_URL = "http://localhost:11434/api/generate"

EMBEDDINGS_MODEL = "ipipan/silver-retriever-base-v1"
COLLECTION_NAME = "OrzeczeniaMLWorkout"

TOP_K = 25
MAX_CONTEXT_CHARS = 3500


def calculate_embedding(text: str):
    payload = {"model": EMBEDDINGS_MODEL, "input": "</s> " + text}
    r = requests.post(EMBEDDINGS_URL, json=payload)
    r.raise_for_status()
    return r.json()["data"][0]["embedding"]


def query_weaviate_by_vector(vector, top_k=TOP_K):
    query = f"""
    query {{
      Get {{
        {COLLECTION_NAME}(
          limit: {top_k},
          nearVector: {{ vector: {json.dumps(vector)} }}
        ) {{
          text
          source_file
          _additional {{ distance }}
        }}
      }}
    }}
    """
    r = requests.post(WEAVIATE_GRAPHQL_URL, json={"query": query})
    r.raise_for_status()
    data = r.json()
    return data["data"]["Get"][COLLECTION_NAME]


def build_prompt(user_question: str, contexts: list):
    system_note = (
        """
Asystent analizy orzeczniczej — PROTOKÓŁ RESPONDENTA (TWARDY TRYB):

Udzielasz odpowiedzi WYŁĄCZNIE na podstawie przekazanych fragmentów orzeczeń.
Zakaz tworzenia nowych źródeł, komentarzy, list orzeczeń, streszczeń ogólnych.
Zakaz odwoływania się do stanowisk stron — analizujesz TYLKO stanowisko SĄDU.

OBOWIĄZKOWY FORMAT ODPOWIEDZI:

KROK 1: Werdykt (A / B / BRAK DANYCH)

KROK 2: Uzasadnienie oparte WYŁĄCZNIE na stanowisku SĄDU (bez treści własnych)

KROK 3: Wyłącznie cytaty SĄDU z fragmentów [N], dotyczące:
- obiektów tymczasowych,
- art. 29 PB,
- art. 41 PB,
- prac przygotowawczych,
- wymogu pozwolenia na budowę.

KROK 4: Nic poza powyższymi krokami.

Dopuszczalne są jedynie cytaty i parafrazy stanowiska SĄDU z odwołaniem [N].
Zakaz generowania jakichkolwiek list orzeczeń lub dodatkowych analiz.
        """
    )

    joined = []
    for i, c in enumerate(contexts, start=1):
        snippet = shorten(
            c["text"],
            width=int(MAX_CONTEXT_CHARS / max(1, len(contexts))),
            placeholder=" [...]"
        )
        joined.append(f"[{i}] {c['source_file']}:\n{snippet}\n")

    return (
        f"{system_note}\n\n"
        f"Pytanie: {user_question}\n\n"
        f"Dostępne fragmenty:\n" + "\n\n".join(joined)
    )


def generate_answer_bielik(prompt: str):
    payload = {"model": "SpeakLeash/bielik-7b-instruct-v0.1-gguf", "prompt": prompt, "stream": False}
    r = requests.post(OLLAMA_URL, json=payload)
    r.raise_for_status()
    return r.json()["response"]


def main():
    if len(sys.argv) < 2:
        print("Brak pytania")
        return

    user_q = sys.argv[1]
    emb = calculate_embedding(user_q)
    hits = query_weaviate_by_vector(emb)
    prompt = build_prompt(user_q, hits)
    answer = generate_answer_bielik(prompt)

    print(answer)


if __name__ == "__main__":
    main()
