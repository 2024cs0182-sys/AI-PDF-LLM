import numpy as np


def create_embeddings(chunks):
    """
    Temporary lightweight embedding replacement.

    Creates deterministic vectors from text so the
    application can run on a low-memory deployment.
    """

    vectors = []

    for chunk in chunks:

        vector = np.zeros(384, dtype=np.float32)

        encoded = chunk.lower().encode(
            "utf-8",
            errors="ignore"
        )

        for i, value in enumerate(encoded[:384]):
            vector[i] = value / 255.0

        vectors.append(vector)

    return np.array(vectors, dtype=np.float32)


def create_query_embedding(query):

    vector = np.zeros(384, dtype=np.float32)

    encoded = query.lower().encode(
        "utf-8",
        errors="ignore"
    )

    for i, value in enumerate(encoded[:384]):
        vector[i] = value / 255.0

    return vector