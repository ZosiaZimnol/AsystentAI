from openai import OpenAI
from pathlib import Path
import weaviate 
import pdfplumber
from weaviate.classes.config import Configure, Property, DataType, VectorDistances

# -----------------------------
# KONFIGURACJA KLIENTA
# -----------------------------
CLIENT = OpenAI(
    base_url="http://localhost:8085/v1",
    api_key="ml-workout"   # wymagany przez bibliotekę, ale ignorowany przez serwer
)


# -----------------------------
# 1. EMBEDDING
# -----------------------------
def calculate_embedding(text: str):
    prepared_input = "</s> " + text

    response = CLIENT.embeddings.create(
        input=prepared_input,   
        model="ipipan/silver-retriever-base-v1"
    )

    return response.data[0].embedding


# -----------------------------
# 2. WCZYTYWANIE PLIKÓW
# -----------------------------
import pdfplumber

def load_legal_texts(data_path: str):
    texts = []
    for file in sorted(Path(data_path).glob("*")):
        if file.suffix.lower() == ".txt":
            texts.append(file.read_text(encoding="utf-8"))

        elif file.suffix.lower() == ".pdf":
            with pdfplumber.open(file) as pdf:
                content = ""
                for page in pdf.pages:
                    content += page.extract_text() + "\n"
            texts.append(content)

        else:
            print(f"⚠️ Pomijam nieobsługiwany plik: {file.name}")

    return texts



# -----------------------------
# 3. CHUNKING TEKSTU
# -----------------------------
def  chunk_text(text, chunk_size=700, chunk_overlap=120):
    """
    Dzieli tekst na fragmenty (chunk_size) z overlapem.
    Dokładnie tak jak w filmiku!
    """
    chunks = []

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += (chunk_size - chunk_overlap)  # przesuwamy się o chunk_size - overlap

    return chunks


# -----------------------------
# 4. GŁÓWNY FLOW
# -----------------------------
# wczytaj orzeczenia
texts = load_legal_texts("./orzeczenia")

print(f"Wczytano {len(texts)} plików.")

all_embeddings = []

for idx, text in enumerate(texts):
    print(f"\n--- Przetwarzam orzeczenie {idx+1} ---")

    # chunking – MUSI BYĆ 700/120 w obu miejscach!
    chunks = chunk_text(text, chunk_size=700, chunk_overlap=120)
    print(f"Liczba chunków: {len(chunks)}")

    for chunk in chunks:
        emb = calculate_embedding(chunk)
        all_embeddings.append(emb)

print("\nŁączna liczba embeddingów:", len(all_embeddings))
print("Długość pojedynczego embeddingu:", len(all_embeddings[0]))

# -----------------------------
# 5. POŁĄCZENIE Z WEAVIATE
# -----------------------------
DB_CLIENT = weaviate.connect_to_local(
    host="localhost",
    port=8080,
    grpc_port=50051,
    skip_init_checks=True
)


COLLECTION_NAME = "OrzeczeniaMLWorkout"

# Jeśli kolekcja istnieje — usuń (czyści bazę przed nowym importem)
try:
    DB_CLIENT.collections.delete(COLLECTION_NAME)
    print("Usunięto istniejącą kolekcję.")
except:
    pass

# -----------------------------
# 6. TWORZENIE KOLEKCJI
# -----------------------------
DB_CLIENT.collections.create(
    name=COLLECTION_NAME,
    properties=[
        Property(name="text", data_type=DataType.TEXT),
        Property(name="source_file", data_type=DataType.TEXT),
    ],
    vector_index_config=Configure.VectorIndex.hnsw(
        distance_metric=VectorDistances.COSINE
    )
)


print("Utworzono kolekcję:", COLLECTION_NAME)

collection = DB_CLIENT.collections.get(COLLECTION_NAME)

# -----------------------------
# 7. ZAPIS DO WEAVIATE
# -----------------------------
print("🔄 Zapisuję dane do Weaviate...")

for text_idx, text in enumerate(texts):
    chunks = chunk_text(text, chunk_size=700, chunk_overlap=120)

    for chunk in chunks:
        emb = calculate_embedding(chunk)

        collection.data.insert(
            properties={
                "text": chunk,
                "source_file": f"orzeczenie_{text_idx+1}.txt"
            },
            vector=emb
        )

print("✔ Zapis zakończony.")

# -----------------------------
# 8. LICZENIE REKORDÓW
# -----------------------------
total_count = collection.aggregate.over_all(
    total_count=True
).total_count

print("📊 Liczba rekordów w kolekcji:", total_count)

DB_CLIENT.close()
