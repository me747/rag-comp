import re
from .data_loader import load_pdf, load_txt

# duplicating sentence splitter from compressor.py instead of importing it, I don't wanna maintain a single func. in compressor.py since these 2 files are conceptually different
def split_into_sent(text):
    # quick sentence splitter to split on . ? ! followed by a space
    #* earlier was splitting only on . ? !, but classical literature usually a lot of dialogues enclosed within "".
    #* so the regex splitter wasn't working as I inteded it to, now added it to allow an optional curly quote character to sit between puncuation & the whitespace before deciding to split.
    sentences = re.split(r'(?<=[.?!])["\u201d\u2019]?\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()] 

    return sentences

# splitting text into smaller pieces to process them, using a fixed-size approach for (sentence-based )
# def chunk_text(text, chunk_size = 500, overlap = 50): # chunk_size & overlap are both in characters for now(& not tokens), simpler to reason about. I'll switch to token-based if this isn't promising

#     chunks = []
#     start = 0 

#     while start < len(text):
#         end = start + chunk_size
#         chunk = text[start:end]

#         chunks.append(chunk)

#         start = start + chunk_size - overlap

#     return chunks

# switching from raw character count chunking to sentence based chunking
def chunk_text(text, chunk_size=500, overlap_sentences=2, max_overlap_chars=200):
    # chunk size is still in characters of a rough target size

    sentences = split_into_sent(text)

    chunks = []
    current_chunk = []
    current_len = 0 

    for sentence in sentences:
        current_chunk.append(sentence)
        current_len += len(sentence)

        if current_len >= chunk_size:
            chunks.append(" ".join(current_chunk))
        # to preserve context overlap last few sentences into current_chunk
            overlap = current_chunk[-overlap_sentences:]
            #* add a cap to the overlap, in case the overlap sentences themselves cross the 500 char limit, new sentence cannot be added
            while len(overlap) > 1 and sum(len(s) for s in overlap) > max_overlap_chars: # atleast keep 1 sentence to preserve continuity
                overlap = overlap[1:]

            current_chunk = overlap
            current_len = sum(len(s) for s in current_chunk)

    # leftover sentences after loop ends
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks    


if __name__ == '__main__':
    '''
    text = load_pdf("data/10050-medicare-and-you.pdf")

    chunks = chunk_text(text)

    print(f"Length of Chunks {len(chunks)}\n")
    print("*****First Chunk*****\n")
    print(chunks[0],"\n")

    print("*****Second Chunk*****\n")
    print(chunks[1])
    '''    
    # prototyping on public domain first using homer's odyssey
    od_text = load_txt("data/the_odyssey.txt")

    od_chunks = chunk_text(od_text)

    print(f"Length of Chunks {len(od_chunks)}\n")
    print("*****First Chunk*****\n")
    print(od_chunks[0],"\n")

    print("*****Second Chunk*****\n")
    print(od_chunks[1])

    

