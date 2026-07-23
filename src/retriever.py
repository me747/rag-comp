# putting chunking, embedding & storage into a single thing that i can call

from .data_loader import load_pdf,load_txt
from .chunker import chunk_text
from .embedder import embed_text
from .vec_storage import VecStorage

def build_idx(txt_path): # decided to prototype on public domain so changing pdf to txt doc
    text = load_txt(txt_path)
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
 
    store = build_idx("data/the_odyssey.txt") # changed test case to match public domain use
    
   # question = "Who is Odysseus's wife?"
   # results = retrieve(store, question)
   # print(f"question: {question}\n")
   # for i, r in enumerate(results):
   #     print(f"***result {i+1}***")
   #     print(f"{r}\n")
    
    '''
    added this test case after running the baseline, for q4 the LLM was unable to answer this even though Telemachus is constantly mentioned acros the narration 
    & the model answering there is no mention of Odysseus's own son" almost certainly seems like a retrieval failure, not a generation failure, so doing a manual quick check
    '''
    test_question = "Who is Odysseus's son?"
    results = retrieve(store, test_question)
    print(f"question: {test_question}\n")
    for i, r in enumerate(results):
        print(f"***result {i+1}***")
        print(f"{r}\n")
    
        

