import os
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from handlers.exceptions import ChunkingError, EmbeddingError, RetrieverError

class PDFQA:
    def __init__(self, text: str, api_key: str):
        self.text = text
        self.vector_store = None
        self.retriever = None
        self.embedding_model = OpenAIEmbeddings(
            api_key=api_key,
            model=os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-large")
        )
        self._process_pdf()

    def _split_text(self, text: str) -> list[LCDocument]:
        """Hybrid chunking: semantic chunker first, then recursive splitter for finer granularity"""

        try:
            # SemanticChunker: captures high-level semantic splits
            semantic_splitter = SemanticChunker(
                embeddings=self.embedding_model,
                buffer_size=4,
                add_start_index=False,
                breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=85,
                number_of_chunks=None,
                sentence_split_regex=r"(?<=[.?!])\s+"
            )
            semantic_docs = semantic_splitter.create_documents([text])

            # RecursiveCharacterTextSplitter: further split large semantic chunks
            final_chunks: list[LCDocument] = []
            recursive_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,     
                chunk_overlap=150
            )
            for doc in semantic_docs:
                small_chunks = recursive_splitter.split_text(doc.page_content)
                for chunk in small_chunks:
                    final_chunks.append(LCDocument(
                        page_content = chunk,
                        metadata = doc.metadata
                    ))

            if not final_chunks:
                raise ChunkingError("No text chunks were created from the input text.")
                
            return final_chunks
        except Exception as e:
            raise ChunkingError(f"Text chunking failed: {str(e)}") from e

    def _embed_texts(self, splits: list[LCDocument]) -> FAISS:
        """Embed and create FAISS vector store"""
        try:
            if not splits:
                raise EmbeddingError("No text splits provided for embedding.")
            vector_store = FAISS.from_documents(splits, self.embedding_model)
            return vector_store
        except Exception as e:
            raise EmbeddingError(f"Embedding creation failed: {str(e)}") from e


    def _process_pdf(self):
        """Split, embed, and create hybrid retriever"""
        try:
            splits = self._split_text(self.text)
            self.vector_store = self._embed_texts(splits)

            # Dense FAISS retriever
            dense_retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 12, "fetch_k": 50, "lambda_mult": 0.7}
            )

            # Sparse BM25 retriever
            bm25_retriever = BM25Retriever.from_documents(splits)

            # Hybrid ensemble retriever
            hybrid_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, dense_retriever],
                weights=[0.35, 0.65]  # adjust weighting as needed
            )

            self.retriever = hybrid_retriever
        except Exception as e:
            raise RetrieverError(f"Retriever setup failed: {str(e)}") from e

# def rag_retriever() -> ContextualCompressionRetriever:
#     if "pdf_qa" not in st.session_state:
#         raise ValueError("⚠️ Please upload and process a PDF first.")
#     return st.session_state.pdf_qa.retriever
