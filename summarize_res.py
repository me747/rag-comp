import json
import sys

def summarize(results_path):
    with open(results_path) as f:
        results = json.load(f)

    avg_uncompressed = sum(r["uncompressed_score"] for r in results) / len(results)
    avg_compressed = sum(r["compressed_score"] for r in results) / len(results)
    total_input_uncompressed = sum(r["uncompressed_input_tokens"] for r in results)
    total_input_compressed = sum(r["compressed_input_tokens"] for r in results)

    print(f"file: {results_path}")
    print(f"questions: {len(results)}")
    print(f"avg score - uncompressed: {avg_uncompressed:.2f}, compressed: {avg_compressed:.2f}")
    print(f"total input tokens - uncompressed: {total_input_uncompressed}, compressed: {total_input_compressed}")

    token_savings = total_input_uncompressed - total_input_compressed
    pct_savings = (token_savings / total_input_uncompressed) * 100
    print(f"token savings: {token_savings} ({pct_savings:.1f}%)")

if __name__ == "__main__":
    summarize(sys.argv[1])