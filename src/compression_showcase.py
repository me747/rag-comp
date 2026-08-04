# picking a few questions to show what compression keeps/drops on the REAL retrieved chunks. No api calls here, just retrieval + compression, so its a free rerun
import json
from .retriever import build_idx, retrieve
from .compressor import compress_chunk

def showcase(txt_path, questions, k=5, threshold=0.3):
    store = build_idx(txt_path)

    all_results = []

    for question in questions:
        print(f"\n***{question}***")

        retrieved_chunks = retrieve(store, question, k=k)

        question_result = {"question": question, "chunks": []}

        for i, chunk in enumerate(retrieved_chunks):
              compressed_text, kept, dropped = compress_chunk(chunk, question, threshold=threshold)

              print(f"\n***chunk{i+1}***")

              print(f"kept {len(kept)}")
              for s in kept:
                   print(f" + {s}")

              print(f"dropped {len(dropped)}")
              for s in dropped:
                   print(f" - {s}")

              question_result["chunks"].append({
                   "original_chunk": chunk,
                   "kept": kept,
                   "dropped": dropped
              })

        all_results.append(question_result)
    return all_results      

             
if __name__ == '__main__':
     ques_to_display = [
          "Who is Odysseus's wife?",
          "Who are the suitors trying to marry?",
          # "What example from the text shows how everyday objects or customs are described realistically?" I used this question during my initial test runs 
          # but it feels very open ended and out of current project scope
          "What does Circe turn Odysseus's men into?" #  "What does Circe turn Odysseus's men into when they first arrive at her island?". Rephrasing question to see how a small change in the query embedding affects retrieval
     ]

     results = showcase("data/the_odyssey.txt", ques_to_display)

     with open("compression_showcase.json", "w") as f:
          json.dump(results, f, indent=2)

     print(f"\n saved sentence-level kept/dropped data to compression_showcase.json")
