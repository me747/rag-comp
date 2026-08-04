# RAG Context Compression

A retrieval-augmented generation (RAG) pipeline that compresses retrieved context
before sending it to the LLM, and measures whether that compression hurts or
helps answer accuracy while reducing token usage & cost.

Exploring the idea of working within a resource budget (token budget in this case) rather than just optimizing for raw accuracy.

## Status: Work in progress

Full pipeline (retrieval -> compression -> generation -> LLM-as-judge
evaluation) is working end-to-end and has been validated + iterated on
through two full experiment runs on a public domain prototype dataset.
Next up: explore a few more targeted improvements to retrieval quality.

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

1. `data_loader.py` - extracts text from PDF documents
2. `chunker.py` - splits text into overlapping chunks, respecting sentence
   boundaries (see chunking strategy findings below - this replaced an
   earlier fixed-size overlappingcharacter chunker)
3. `embedder.py` - embeds text using `all-MiniLM-L6-v2`
4. `vector_store.py` - FAISS index for similarity search
5. `retriever.py` - retrieves top-k chunks for a question
6. `compressor.py` - trims retrieved chunks down to question-relevant
   sentences only, using per-sentence embedding similarity against the
   question
7. `generator.py` - sends retrieved content + question to the LLM, returns generated answer & tracks token usage
8. `run_baseline.py` - runs a full Q/A set through retrieval + generation, saves results (question, expected vs. generated answer, token counts) to a results file. (only uncompressed version)
9. `evaluator.py` - LLM-as-judge grading both the uncompressed and
   compressed generated answers against the hand-written expected answer,
   in a single call per question
10. `run_experiment.py` - runs the full QA set through both
   compressed and uncompressed conditions, produces a results table
11. `summarize_res.py` - standalone script that reads saved results file & prints average scores + token savings
12. `compression_showcase.py` / `render_showcase.py` - pulls only real retrieved chunks for a handful of chosen questions and renders an HTML page showing which sentences were
    kept (green) vs. dropped (struck through), per chunk

## Findings so far

*(keeping this updated as I progress)*

**Retrieval Quality:**

- While testing & running with `retriever.py`, I noticed that retrieval quality on the Medicare handbook was decent but not perfect
  with basic similarity search.
  For a direct test question that I used "What does
  Medicare Part B cover?", the correct section is retrieved(but was ranked 2nd instead of 1st), but 1-2 of the
  other top-k results were nearby without directly answering the
  question (e.g., pulling in an "employer coverage" section & a section containing "What isn't covered by Part B" for a "what does
  Part B cover" question).  
  I don't think this is necessarily a bug but expected
  behavior for embedding similarity search, it means some of what gets
  retrieved is noise, which is part of the motivation for the compression
  step.
- Fixed-size character chunking cuts sentences mid-word at chunk
  boundaries. Doesn't break retrieval, but is a known rough edge
  worth mentioning.
- Relational questions(X's Y kinda questions) are a weak spot for chunk-based
  retrieval. From my baseline test Question #4 "Who is Odysseus's son?" consistently failed to retrieve
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
- For "Who is Odysseus's wife?", the chunk that most directly answers the
  question came back ranked 5th out of 5 with the original chunker,
  behind several chunks only loosely wife/marriage-adjacent.
  **Confirmed this isn't a sorting bug.** Checked `vec_storage.py`
  directly & FAISS `IndexFlatL2` correctly returns nearest-distance-first. 
  Dense embedding similarity doesn't reliably separate "direct answers to a
  question" from "topically nearby" i.e. same underlying limitation as the
  Telemachus/"son" miss.
- **Same pattern confirmed a third time** with "What does Circe turn
  Odysseus's men into?" the correct passage (Eurylochus warning the men
  Circe will "turn us all into pigs or wolves or lions") ranked 5th at
  k=5 with the original chunker.

**Text Cleanup:**
- Gutenberg plain-text files need their own cleanup step. License
  boilerplate at the start/end is easy to strip via the standard
  `*** START/END OF THE PROJECT GUTENBERG EBOOK ***` markers, but this
  particular edition also had a large footnotes section tacked onto the
  end which was getting chunked and embedded as if it were the actual narrative text & was actually ranking as a
  top-1 retrieval result for an unrelated question before I stripped it out.
- Manually moved the start marker past the title/table-of-contents/
  dedication block, since that's pure navigation noise, not content,
  simpler than writing code to strip it, at the cost of this being a
  manual one-time fix rather than something `load_txt()` handles
  automatically on a fresh download.
- Found and fixed two sentence-splitting bugs that were quietly merging
  distinct sentences together during compression:
  - Dialogue ending in a curly closing quote (e.g. `footstool."`) wasn't
    splitting correctly, since the split regex only matched punctuation
    immediately followed by whitespace. Fixed by allowing an optional
    closing quote character in the pattern.
  - All-caps chapter/section headers (e.g. "BOOK XXIII") have no ending
    punctuation, so they were getting glued onto whichever sentence came
    next. Fixed with a cleanup pass that adds a period after any ALL-CAPS
    line missing one. Decided to keep headers as their own clean sentences
    (rather than stripping them entirely) since headers could carry real
    signal.
  - Found a related issue after fixing the above: inline footnote
    reference numbers glued directly onto words with no space (e.g.
    "Strait128", "seats.3", "them.179"), leftover artifacts of the
    original superscript footnote markers. Stripped these out too, since
    this translation always spells real numbers as words.
- Verified both sentence-splitting fixes worked using compression
  showcase script a chunk that previously had Penelope's recognition
  scene glued to a "BOOK XXIII" header now isolates cleanly.  

**Translation Specific Vocabulary:** 
- This particular translation by Butler used "Ulysses" almost
  exclusively instead of "Odysseus". Despite my Q/A set using "Odysseus"
  embedding-based retrieval still picked the right "Ulysses" passages in
  most cases, and the LLM correctly identified the two as the same
  character in its answers rather than getting confused or saying it
  couldn't find "Odysseus" in the text.

**Experiment Results:**
  **First Experiment Run:**
  - First full baseline run (uncompressed, on the Odyssey prototype set)
  ran cleanly**, 15/15 questions ran without errors, token usage
  per question ranged roughly between 700-850 input & 30-300 output tokens. 
  Most answers were well-grounded with direct quotes from context & the model
  correctly said "I don't know based on the provided context" on 2
  questions where the answer genuinely wasn't retrievable, rather than
  hallucinating.

  **Experiment comparison: original chunker vs. sentence-aware chunker**

  | | Original chunker | Sentence-aware chunker |
  |---|---|---|
  | Avg score - uncompressed | 0.57 | 0.53 |
  | Avg score - compressed | 0.53 | 0.57 |
  | Total input tokens - uncompressed | 11,377 | 13,472 |
  | Total input tokens - compressed | 8,131 | 9,313 |
  | Token savings | 28.5% | 30.9% |
  | Questions matching between conditions | 14/15 | 13/15 |

  **Chunking strategy change:**
- Switched `chunker.py` from fixed-size character chunking to sentence-
  based chunking (groups whole sentences up to a soft target size, never
  cuts mid-sentence/mid-word; overlap is now a capped number of trailing
  sentences instead of a fixed character count).
 - Found and fixed a bug in the first version of this: a couple of
  unusually long sentences in the preface could make the carried-over
  overlap alone exceed the chunk-size target, causing the next chunk to
  close almost immediately and produce near-duplicate chunks (inflated
  chunk count from ~1392 to 2334 before the fix; capping overlap length
  brought it back down to ~1558, which I'd assume is a reasonable increase for respecting
  sentence boundaries). 
- **Result: chunking change was not uniform improvement and it only redistributes
  which facts are easy vs. hard to retrieve, not a strict upgrade.**
  - The Circe pig-transformation passage improved from rank 5 to rank 3,
    confirmed reproducible across two different phrasings of the same
    question.
  - The Telemachus/"son" question improved from INCORRECT to
    PARTIALLY_CORRECT.
  - But a previously-correct question ("What is suggested about
    Penelope's behavior toward the suitors?") regressed from CORRECT to
    INCORRECT in both conditions. Verified via `retriever.py` - the specific
    passage needed (Minerva prompting Penelope to show herself to the
    suitors while "feigning a mocking laugh") no longer appears in the
    top 10 results at all after re-chunking.
  - Rerunning the full experiment with the new chunker: scores flipped
    (0.53 uncompressed / 0.57 compressed, versus 0.57/0.53 originally),
    and token savings percentage increased slightly (28.5% -> 30.9%), but
    absolute token counts on both sides went up too(somewhat expected) because sentence-aware
    chunking avoids truncation but produces somewhat larger average
    chunks than the fixed 500-char target, since a chunk only closes after
    finishing its current sentence. 
- Takeaway: better chunking is stil worth doing (fixes real truncation bugs,
  demonstrably improves ranking for some facts) but isn't a silver bullet
  for retrieval quality.

**Eval-set design issues found: (not pipeline failures)**
- One question asked for "an example" of realistic everyday detail
  (originally about sandals; later swapped in the showcase for a more
  specific single-answer version, "How does the text describe the mixing
  of wine at meals?" - then realized this one has the same problem, since
  the wine-mixing custom repeats many times in the text & the example question was too open-ended and my Q/A pairs only mention a single correct answer (while many exist). settled on using "What does Circe turn Odysseus's men into?" as a cleaner single-answer
  replacement for showcase testing). Original question kept as-is in the
  real QA set for comparability across the 2 experiments.
- Eumaeus's hut location question: expected answer phrasing ("high above
  the sea, wide view") doesn't exactly match the actual text ("a site
  which could be seen from far") was written from general memory of
  the odyssey rather than this exact passage, a lesson for writing future
  QA pairs directly against source text.
