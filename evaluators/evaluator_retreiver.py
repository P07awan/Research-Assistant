import numpy as np
import os
from typing import Any
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document as LCDocument

# ==============================
# Evaluation Functions
# ==============================

class RetrieverEvaluator:
    """
    Evaluates a RAG retriever (e.g., PDFQA.retriever) against a benchmark of queries and golden answers.
    Supports Recall@k, Precision@k, F1, and cosine similarity.
    """

    def __init__(self, retriever: Any, embedding_model_name: str ="text-embedding-3-large"):
        """
        retriever: Your PDFQA.retriever object
        embedding_model_name: Name of the embedding model for cosine similarity
        """
        self.retriever = retriever
        self.embed_model = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDINGS_MODEL", embedding_model_name)
        )

    def _compute_cosine_similarity(self, text1, text2):
        embeddings = self.embed_model.embed_documents([text1, text2])
        emb1 = np.array([embeddings[0]])
        emb2 = np.array([embeddings[1]])
        return cosine_similarity(emb1, emb2)[0][0]

    def evaluate(self, benchmark: list[dict[str, str]], k: int , similarity_threshold: float):
        """
        benchmark: list of dicts, each with 'query' and 'answer' keys
        k: top-k retrieved chunks to consider
        similarity_threshold: minimum cosine similarity to count as "relevant"
        """
        from typing import List

        recall_scores: List[int] = []
        precision_scores: List[float] = []
        f1_scores: List[float] = []
        semantic_sims: List[float] = []

        for item in benchmark:
            query = item["query"]
            golden_answer = item["answer"]

            # Retrieve top chunks from PDFQA retriever
            retrieved_docs: list[LCDocument] = self.retriever.get_relevant_documents(query)
            topk_docs = retrieved_docs[:k]
            retrieved_texts = [doc.page_content for doc in topk_docs]

            # Compute semantic similarity for each retrieved chunk
            sims = [self._compute_cosine_similarity(golden_answer, text) for text in retrieved_texts]
            semantic_sims.append(max(sims) if sims else 0)  # Take max similarity

            # Determine which chunks are "relevant"
            relevant_flags = [1 if s >= similarity_threshold else 0 for s in sims]

            # Recall@k: did we retrieve at least one relevant chunk?
            recall = 1 if sum(relevant_flags) > 0 else 0
            recall_scores.append(recall)

            # Precision@k: proportion of retrieved chunks that are relevant
            precision = sum(relevant_flags) / len(relevant_flags) if len(relevant_flags) > 0 else 0
            precision_scores.append(precision)

            # F1 Score
            if precision + recall == 0:
                f1 = 0
            else:
                f1 = 2 * (precision * recall) / (precision + recall)
            f1_scores.append(f1)

        # Aggregate results
        results = {
            "Recall@k": np.mean(recall_scores),
            "Precision@k": np.mean(precision_scores),
            "F1@k": np.mean(f1_scores),
            "MaxCosineSim": np.mean(semantic_sims),
        }

        return results
