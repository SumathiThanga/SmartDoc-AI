import faiss
import numpy as np
import json
from pathlib import Path

VECTOR_STORE_FOLDER = Path("vector_store")
def create_vector_store(chunks,embeddings):
    vectors = np.array(embeddings,dtype=np.float32)
    #normalise
    faiss.normalize_L2(vectors)
    dimension = vectors.shape[1]
    #create faiss index
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)
    VECTOR_STORE_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )
    faiss.write_index(
        index,
        str(VECTOR_STORE_FOLDER / "faiss.index")
    )
    with open(
        VECTOR_STORE_FOLDER / "chunks.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nFAISS index created successfully!")

    print("Total vectors stored:", index.ntotal)

    print("Vector dimensions:", dimension)

    return index