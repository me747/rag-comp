import json
from .retriever import build_idx, retrieve
from .gen_anthro import gen_answer

def run_baseline(txt_path, qa_path):

    store = build_idx(txt_path)

    with open(qa_path) as f:
        qa_pairs = json.load(f)
    
    results = []

    for pair in qa_pairs:
        question = pair["question"]
        print(f"Question asked: {question}")

        retrieved_chunks = retrieve(store, question, k=5)
        generated_res = gen_answer(question, retrieved_chunks)

        print(f"Answer received: {generated_res['answer'][:150]}")
        
        results.append({
            "id": pair["id"],
            "question": question,
            "expected_answer": pair["answer"],
            "generated_answer": generated_res["answer"],
            "input_tokens": generated_res["input_tokens"],
            "output_tokens": generated_res["output_tokens"]
        })
    
    return results

if __name__ == "__main__":
    results = run_baseline("data/the_odyssey.txt", "data/od_qa_pairs.json")
    
    # dumping raw results to a file 
    with open("baseline_results_odyssey.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\ndone, ran {len(results)} questions, saved to baseline_results_odyssey.json")
