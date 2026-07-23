import re
import numpy as np
from .embedder import embed_text

def split_into_sent(text):
    # quick sentence splitter to split on . ? ! followed by a space
    sentences = re.split(r'(?<=[.?!])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()] # remove emptry strings that sometimes show up 

    return sentences

def cosine_similarity(vec1, vec2):
    # measuring how similar two vectors are
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    return dot_product / (norm1*norm2)

def compress_chunk(chunk_text, question, threshold=0.3):
    # threshold decides the cutoff, lower keeps more & higher keeps less, using 0.3 as a starting point

    sentences = split_into_sent(chunk_text)

    if len(sentences) == 0: # early return guard
        return "", [], []

    question_embedding = embed_text(question)[0]
    sentence_embeddings = embed_text(sentences)

    # keeping track of kept & dropped sentences
    kept_sentences = []
    dropped_sentences = []

    for sentence, sent_embedding in zip(sentences, sentence_embeddings):
        similarity = cosine_similarity(question_embedding, sent_embedding)

        if similarity >= threshold:
            kept_sentences.append(sentence)
        else:
            dropped_sentences.append(sentence)

    compressed_text = " ".join(kept_sentences)

    return compressed_text, kept_sentences, dropped_sentences        

def compress_mul_chunks(chunks, question, threshold=0.3):
    # to run compression across all retrieved chunks 
    all_compressed = []
    all_kept = []
    all_dropped = []

    for chunk in chunks:
        compressed, kept, dropped = compress_chunk(chunk, question, threshold)
        all_compressed.append(compressed)
        all_kept.extend(kept)
        all_dropped.extend(dropped)

    return all_compressed, all_kept, all_dropped

if __name__ == '__main__':
    # added the line "She had many suitors pressing her to remarry, believing her husband woulld never come home" after the initial run, to test against a harder case 
    # I think this line is still about Penelope's marital situation (but never actually names Odysseus/Ulysses)
    # seems like an ambigious enough case because:
    # a) if its kept: the model's picking up the marital theme even without the name (which is arguabaly still useful context)
    # b) if its dropped: the threshold could be too strict about directness & favoring "answers that match the question" over "something that is topically related to the question."


    fake_chunk = """Penelope is the wife of Ulysses, and she has waited twenty years for his return.
    She had many suitors pressing her to remarry, believing her husband would never come home.          
    The suitors feast every day in the halls, eating up the substance of the house.
    Telemachus grew angry when he saw the wooers behaving so badly.
    Eumaeus kept his hut high upon the cliffs, looking out over the wide sea.
    Minerva often came to Ithaca disguised as a stranger to help Telemachus."""

    question = "Who is Penelope married to?"

    compressed, kept, dropped = compress_chunk(fake_chunk, question, threshold=0.3)

    print("KEPT:")
    for s in kept:
        print(f"  + {s}")

    print("\nDROPPED:")
    for s in dropped:
        print(f"  - {s}")

    print(f"\ncompressed text: {compressed}")