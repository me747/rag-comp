# main script runs every question through both uncompressed and compressed context, judges the answers, and saves everything

import json 
from .retriever import build_idx, retrieve
from .gen_anthro import gen_answer
from .compressor import compress_mul_chunks
from .evaluator import judge_ans, score_verdict

def run_full_exp(txt_path, qa_path, threshold=0.3):
    store = build_idx(txt_path)

    with open(qa_path) as f:
        qa_pairs = json.load(f)

    results = []

    for pair in qa_pairs:
        question = pair["question"]
        expected = pair["answer"]
        print(f"\n*** Question {pair['id']}: {question} ***")

        retrieved_chunks = retrieve(store, question, k=5)

        # uncompressed basline
        uncompressed_res= gen_answer(question, retrieved_chunks)

        # compressed 
        compressed_chunks, kept, dropped = compress_mul_chunks(retrieved_chunks, question, threshold=threshold)
        compressed_res = gen_answer(question, compressed_chunks)

        # judging both answers in one call 
        verdict_uncompressed, verdict_compressed = judge_ans(
            question, expected, uncompressed_res["answer"], compressed_res["answer"]
        )

        print(f"  uncompressed: {verdict_uncompressed} | compressed: {verdict_compressed}")

        results.append({
            "id": pair["id"],
            "question": question,
            "expected_answer": expected,
            "uncompressed_answer": uncompressed_res["answer"],
            "uncompressed_input_tokens": uncompressed_res["input_tokens"],
            "uncompressed_output_tokens": uncompressed_res["output_tokens"],
            "uncompressed_verdict": verdict_uncompressed,
            "uncompressed_score": score_verdict(verdict_uncompressed),
            "compressed_answer": compressed_res["answer"],
            "compressed_input_tokens": compressed_res["input_tokens"],
            "compressed_output_tokens": compressed_res["output_tokens"],
            "compressed_verdict": verdict_compressed,
            "compressed_score": score_verdict(verdict_compressed),
            "num_sentences_kept": len(kept),
            "num_sentences_dropped": len(dropped)
        })
        # saving progress after every question, so a crash doesn't cause total loss (learned this the hard way)
        with open("experiment_results_odyssey.json", "w") as f:
                json.dump(results, f, indent=2)
    
    return results

if __name__ == '__main__':
    results = run_full_exp("data/the_odyssey.txt", "data/od_qa_pairs.json")

    print(f"\ndone, ran {len(results)} questions through both conditions")
    print(f"saved full results to experiment_results_odyssey.json")