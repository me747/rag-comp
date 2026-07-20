from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# turning text into vectors for similarity checks down the line, using "all-MiniLM-L6-v2" as its small & fast and I think its good a starting point
def embed_text(texts):
    # texts can be a single string or a list of strings
    if isinstance(texts, str):
        texts = [texts]

    embeddings = model.encode(texts)
    return embeddings

if __name__ == '__main__':
    test_sentences = ["Meeting your health care needs", "Medicare now pays for Advanced Primary Care Management services each"]
    vecs = embed_text(test_sentences)
    print(f"Shape of vector {vecs.shape}")
