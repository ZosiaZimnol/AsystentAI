model=ipipan/silver-retriever-base-v1
volume=$PWD/embedding_model_data

docker run -p 8085:80 -v $volume:/data --pull always ghcr.io/huggingface/text-embeddings-inference:cpu-1.8 --model-id $model