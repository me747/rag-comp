# RAG Context Compression

A retrieval-augmented generation (RAG) pipeline that compresses retrieved context
before sending it to the LLM, and measures whether that compression hurts or
helps answer accuracy while reducing token usage & cost.

Exploring the idea of working within a resource budget (token budget in this case) rather than just optimizing for raw accuracy.

## Status: Work in progress

Currently through Phase 1 (retrieval). Generation, compression, and the full
compressed-vs-uncompressed experiment are still in progress.

## Current idea

Standard RAG: retrieves relevant chunks from a document -> stuff them into a
prompt -> generate an answer. 
This project experiments with adding a new step: before the chunks go to the LLM, 
each retrieved chunk is filtered sentence-by-sentence, keeping
only the sentences that are actually relevant to the specific question being
asked (based on embedding similarity to the question).  
The rest gets dropped.  

Something I'm trying to work through is that: **does trimming irrelevant
sentences out of the retrieved context reduce token cost without hurting
answer quality?**

## Pipeline (*so far*)

1. `data_loader.py` — extracts text from PDF documents
2. `chunker.py` — splits text into fixed-size overlapping chunks
3. `embedder.py` — embeds text using `all-MiniLM-L6-v2`
4. `vector_store.py` — FAISS index for similarity search
5. `retriever.py` — retrieves top-k chunks for a question
6. `compressor.py` — *(in progress)* trims retrieved chunks down to
   question-relevant sentences only
7. `generator.py` — *(in progress)* sends context + question to the LLM,
   tracks token usage
8. `evaluator.py` — *(in progress)* LLM-as-judge grading of generated
   answers against hand-written expected answers
9. `run_experiment.py` — *(in progress)* runs the full QA set through both
   compressed and uncompressed conditions, produces a results table

## Findings so far

*(keeping this updated as I progress)*

- **While testing & running with `retriever.py`, I noticed that retrieval quality on the Medicare handbook was decent but not perfect
  with basic similarity search.** 
  For a direct test question that I used "What does
  Medicare Part B cover?", the correct section is retrieved(but was ranked 2nd instead of 1st), but 1-2 of the
  other top-k results were nearby without directly answering the
  question (e.g., pulling in an "employer coverage" section & a section containing "What isn't covered by Part B" for a "what does
  Part B cover" question).  
  I don't think this is necessarily a bug but expected
  behavior for embedding similarity search, it means some of what gets
  retrieved is noise, which is part of the motivation for the compression
  step.
- **Fixed-size character chunking cuts sentences mid-word at chunk
  boundaries.** Doesn't break retrieval, but is a known rough edge
  worth mentioning.

