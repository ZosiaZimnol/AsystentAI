📘 README.md – AsystentAI (RAG z Bielikiem + Weaviate)
AsystentAI – System Analizy Orzecznictwa oparty o RAG (Bielik + Weaviate + Silver Retriever)

Ten projekt umożliwia zadawanie pytań prawnych i otrzymywanie odpowiedzi opartych wyłącznie na rzeczywistych fragmentach orzeczeń, dzięki technologii RAG (Retrieval-Augmented Generation).

System działa lokalnie i NIE wymaga żadnych płatnych usług (OpenAI itp.).

🚀 1. Co potrafi AsystentAI?

odpowiada na pytania tylko na podstawie znalezionych orzeczeń,

przytacza cytaty sądu,

generuje argumentację prawną,

nie halucynuje samodzielnie — korzysta tylko z kontekstu,

pozwala analizować orzeczenia PDF/TXT jak profesjonalny prawnik.

🔧 2. Wymagania

Windows 10 / Windows 11

Docker Desktop

Python 3.10–3.12

Git

Ollama (do uruchamiania Bielika)

Wszystko działa lokalnie.

📥 3. Instalacja krok po kroku
KROK 1 – Pobierz projekt

Otwórz PowerShell:

git clone https://github.com/ZosiaZimnol/AsystentAI.git
cd AsystentAI

KROK 2 – Zainstaluj zależności Pythona
pip install -r requirements.txt

KROK 3 – Uruchom Docker Desktop

Jeśli Docker nie jest włączony → włączyć.

KROK 4 – Uruchom Weaviate

W folderze projektu wpisz:

docker compose up -d

To uruchomi lokalną bazę wektorową Weaviate.

KROK 5 – Pobierz model Bielika
ollama pull SpeakLeash/bielik-7b-instruct-v0.1-gguf

KROK 6 – Wczytaj orzeczenia do bazy

Pliki orzeczeń PDF/TXT muszą znajdować się w folderze:

./orzeczenia


Potem uruchamiasz:

python ingest_data.py


KROK 7 – Zadawanie pytań

Wpisujesz dowolne pytanie prawne:

python rag.py "Czy obiekt tymczasowy wymaga pozwolenia przed uprawomocnieniem decyzji?"


Przykłady:

python rag.py "Przytocz cytat sądu dotyczący art. 41 PB."
python rag.py 'Czy kontener postawiony przed pozwoleniem wymaga zgody?'
python rag.py "Jak Sąd definiuje prace przygotowawcze?"


Model odpowie tylko na podstawie znalezionych orzeczeń.

🧠 4. Jak działa system

Zadajesz pytanie → Silver Retriever tworzy embedding.

Weaviate szuka najlepiej pasujących fragmentów orzeczeń.

Fragmenty trafiają do Bielika.

Bielik odpowiada, używając tylko przekazanych tekstów.

Odpowiedź = prawdziwa analiza oparta na orzeczeniach.
