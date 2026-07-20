import numpy as np 
import faiss # storing embeddings in FAISS, to search them faster, not sure rn if FAISS is overkill for a small dataset. Apparently its a standard tool 

class VecStorage:
    def __init__(self, embedding_dim=384): # output size for MiniLM i.e. 384
        self.index = faiss.IndexFlatL2(embedding_dim) # creating a FAISS index
        self.chunks = [] 

    def add(self, chunks, embeddings):
        """
        Args:
            chunks    : list of broken down text
            embeddings: list of vec. for those text
        """
        self.chunks.extend(chunks)
        self.index.add(np.array(embeddings).astype("float32")) # FAISS accepts NumPy array of 32-bit floats

    def search(self, query_embedding, k=3):
        """
        Args:
            query_embedding: vec. of the query
            k              : no. of results to return
        """
        query_embedding = np.array(query_embedding).astype("float32")
        distances, indices = self.index.search(query_embedding, k) # dist. how far each result is from query, indices pos. of closest vec.

        results = []
        for i in indices[0]: # taking only first query result
            results.append(self.chunks[i]) # now add actual text using index to results
    
        return results