# putting chunking, embedding & storage into a single thing that i can call

from data_loader import load_pdf
from chunker import chunk_text
from embedder import embed_text
from vec_storage import VecStorage

def build_idx(pdf_path):
    text = load_pdf(pdf_path)
    chunks = chunk_text(text)

    print(f"building an index from {len(chunks)} chunks, might take a sec")
    embeddings = embed_text(chunks)

    store = VecStorage()
    store.add(chunks, embeddings)

    return store

def retrieve(store, question, k=5):
    question_embedding = embed_text(question)
    results = store.search(question_embedding, k=k)
    return results

if __name__ == '__main__':
    store = build_idx("data/10050-medicare-and-you.pdf")
    question = "What does Medicare Part B cover"
    results = retrieve(store, question)
    print(f"question: {question}\n")
    for i, r in enumerate(results):
        print(f"***result {i+1}***")
        print(f"{r}\n")
        

