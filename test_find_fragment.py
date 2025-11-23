import requests, json

EMBEDDINGS_URL = "http://localhost:8085/v1/embeddings"
WEAVIATE_URL = "http://localhost:8080/v1/graphql"

phrase = "Usytuowanie obiektu przeznaczonego do czasowego użytkowania"

# 1. embedujemy frazę
r = requests.post(EMBEDDINGS_URL, json={
    "model": "ipipan/silver-retriever-base-v1",
    "input": "</s> " + phrase
})
vector = r.json()["data"][0]["embedding"]

# 2. zapytanie nearVector do Weaviate
query = {
    "query": f"""
    {{
      Get {{
        OrzeczeniaMLWorkout(
          limit: 20,
          nearVector: {{
            vector: {json.dumps(vector)}
          }}
        ) {{
          text
          source_file
          _additional {{ distance }}
        }}
      }}
    }}
    """
}

resp = requests.post(WEAVIATE_URL, json=query)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
