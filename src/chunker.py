from data_loader import load_pdf

# splitting text into smaller pieces to process them, using a fixed-size approach for (sentence-based )
def chunk_text(text, chunk_size = 500, overlap = 50): # chunk_size & overlap are both in characters for now(& not tokens), simpler to reason about. I'll switch to token-based if this isn't promising

    chunks = []
    start = 0 

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start = start + chunk_size - overlap

    return chunks

if __name__ == '__main__':

    text = load_pdf("data/10050-medicare-and-you.pdf")

    chunks = chunk_text(text)

    print(f"Length of Chunks {len(chunks)}\n")
    print("*****First Chunk*****\n")
    print(chunks[0],"\n")

    print("*****Second Chunk*****\n")
    print(chunks[1])


