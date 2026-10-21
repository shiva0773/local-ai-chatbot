
import ollama
import math

MODEL = "nomic-embed-text"

sentences = [
    "How do I reset my password?",
    "I forgot my password. How can I change it?",
    "The weather is sunny today.",
]


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def main():
    vectors = []

    for sentence in sentences:
        result = ollama.embed(
            model=MODEL,
            input=sentence,
        )
        vector = result["embeddings"][0]
        vectors.append(vector)

        print(f"\nText: {sentence}")
        print(f"Embedding dimensions: {len(vector)}")
        print(f"First 5 numbers: {vector[:5]}")

    print("\n--- Similarity comparison ---")

    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            similarity = cosine_similarity(vectors[i], vectors[j])

            print(f"\nSentence A: {sentences[i]}")
            print(f"Sentence B: {sentences[j]}")
            print(f"Cosine similarity: {similarity:.4f}")


if __name__ == "__main__":
    main()
