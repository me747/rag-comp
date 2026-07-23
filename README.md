# RAG Context Compression

A retrieval-augmented generation (RAG) pipeline that compresses retrieved context
before sending it to the LLM, and measures whether that compression hurts or
helps answer accuracy while reducing token usage & cost.

Exploring the idea of working within a resource budget (token budget in this case) rather than just optimizing for raw accuracy.

## Status: Work in progress

Currently through Phase 3 (generation, uncompressed baseline) on a public domain dataset. Compression, evaluation, and the full compressed-vs-uncompressed experiment on the real healthcare data are still in progress.

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

## Prototyping approach

Before running this against real healthcare documents, I'm debugging the
full pipeline on public domain text (Homer's *The Odyssey*, via Project
Gutenberg) so I can sanity-check retrieval and generation quality against
questions I can verify myself, without wasting API calls chasing bugs on the
real dataset.

## Pipeline (*so far*)

1. `data_loader.py` — extracts text from PDF documents
2. `chunker.py` — splits text into fixed-size overlapping chunks
3. `embedder.py` — embeds text using `all-MiniLM-L6-v2`
4. `vector_store.py` — FAISS index for similarity search
5. `retriever.py` — retrieves top-k chunks for a question
6. `compressor.py` — *(in progress)* trims retrieved chunks down to
   question-relevant sentences only
7. `generator.py` — sends retrieved content + question to the LLM, returns generated answer & tracks token usage
8. `run_baseline.py` — runs a full Q/A set through retrieval + generation, saves results (question, expected vs. generated answer, token counts) to a results file
9. `evaluator.py` — *(in progress)* LLM-as-judge grading of generated
   answers against hand-written expected answers
10. `run_experiment.py` — *(in progress)* runs the full QA set through both
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
- **Gutenberg plain-text files need their own cleanup step.** License
  boilerplate at the start/end is easy to strip via the standard
  `*** START/END OF THE PROJECT GUTENBERG EBOOK ***` markers, but this
  particular edition also had a large footnotes section tacked onto the
  end which was getting chunked and embedded as if it were the actual narrative text & was actually ranking as a
  top-1 retrieval result for an unrelated question before I stripped it out.
- **Translation-specific vocabulary affects retrieval and generation, but
  less than expected.** This particular translation by Butler used "Ulysses" almost
  exclusively instead of "Odysseus". Despite my Q/A set using "Odysseus"
  embedding-based retrieval still picked the right "Ulysses" passages in
  most cases, and the LLM correctly identified the two as the same
  character in its answers rather than getting confused or saying it
  couldn't find "Odysseus" in the text.
- **Relational questions(X's Y kinda questions) are a weak spot for chunk-based
  retrieval.** From my baseline test Question #4 "Who is Odysseus's son?" consistently failed to retrieve
  any chunk mentioning Telemachus, even though he's a major & frequently mentioned character. 
  Instead it pulled chunks about other unrelated parent-child relationships in the text (Antiphates & Mantius, Autolycus's
  grandson, Otus & Ephialtes, Orestes). 
  Likely cause: the text usually refers to Telemachus by name without restating "Odysseus's son" in the
  same sentence, so a chunk can be entirely about him and still not
  semantically match a query phrased as "X's son." This will likely fail
  the same way under compression too, since compression is only trimming
  sentences within chunks that were already retrieved & it can't fix a
  chunk that never got retrieved in the first place. 
  Worth noting down(I think) as a documented limitation. (I don't think bumping up k to a higher value would work because lexical similarity is being pulled towards the wrong entity entirely, adding metadata to chunks itself might be helpful but I'm not sure how to do that right now.)
- **First full baseline run (uncompressed, on the Odyssey prototype set)
  ran cleanly**, 15/15 questions ran without errors, token usage
  per question ranged roughly between 700-850 input & 30-300 output tokens. 
  Most answers were well-grounded with direct quotes from context & the model
  correctly said "I don't know based on the provided context" on 2
  questions where the answer genuinely wasn't retrievable, rather than
  hallucinating.


