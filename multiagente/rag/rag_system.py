"""Sistema de RAG (Retrieval-Augmented Generation) com embeddings."""

from typing import List
import chromadb
from sentence_transformers import SentenceTransformer
from multiagente.config.config import Config
from multiagente.rag.knowledge_base import get_all_documents

class RAGSystem:
    """Sistema de recuperação aumentada por geração."""

    def __init__(self):
        """Inicializa o sistema RAG com ChromaDB e embeddings."""
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=Config.CHROMA_PATH)
        self.collection = self._initialize_collection()

    def _initialize_collection(self):
        """Inicializa ou recupera a coleção no ChromaDB."""
        collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        if collection.count() == 0:
            self._populate_collection(collection)

        return collection

    def _populate_collection(self, collection):
        """Popula a coleção com documentos da base de conhecimento."""
        documents = get_all_documents()
        chunk_size = getattr(Config, "CHUNK_SIZE", 300)
        chunk_overlap = getattr(Config, "CHUNK_OVERLAP", 60)
        total_chunks = 0

        for doc in documents:
            content = f"{doc['title']}\n{doc['content']}"
            chunks = self._chunk_text(content, chunk_size=chunk_size, overlap=chunk_overlap)
            embeddings = self.embedding_model.encode(chunks).tolist()

            collection.add(
                ids=[f"{doc['id']}::chunk_{index}" for index in range(len(chunks))],
                embeddings=embeddings,
                documents=chunks,
                metadatas=[{
                    "title": doc["title"],
                    "category": doc["category"],
                    "original_id": doc["id"],
                    "chunk_index": index,
                    "total_chunks": len(chunks),
                } for index in range(len(chunks))]
            )
            total_chunks += len(chunks)

        print(f"Base de conhecimento criada com {len(documents)} documentos e {total_chunks} chunks")

    def _chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        """Divide texto em chunks com sobreposição para preservar contexto."""
        cleaned = " ".join(text.split())
        if len(cleaned) <= chunk_size:
            return [cleaned]

        chunks = []
        start = 0
        while start < len(cleaned):
            end = min(start + chunk_size, len(cleaned))

            if end < len(cleaned):
                sentence_break = cleaned.rfind(". ", start, end)
                space_break = cleaned.rfind(" ", start, end)
                best_break = max(sentence_break, space_break)
                if best_break > start + int(chunk_size * 0.6):
                    end = best_break + 1

            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= len(cleaned):
                break
            start = max(0, end - overlap)

        return chunks

    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Recupera documentos mais relevantes para a consulta.

        Args:
            query: texto de consulta
            top_k: número de documentos a recuperar

        Returns:
            lista de documentos relevantes com scores
        """
        query_embedding = self.embedding_model.encode(query).tolist()

        raw_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=10
        )

        threshold = Config.SIMILARITY_THRESHOLD
        best_by_document = {}

        for doc, dist, meta in zip(
            raw_results["documents"][0],
            raw_results["distances"][0],
            raw_results["metadatas"][0]
        ):
            # Filtra documentos com distância acima do threshold (pouco relevantes)
            if dist > threshold:
                continue

            source_id = meta.get("original_id", "unknown")
            candidate = {
                "content": doc,
                "title": meta.get("title", "Unknown"),
                "category": meta.get("category", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "distancia": dist,
                "distance": dist,
                "relevance_score": max(0.0, 1 - dist),
            }

            current = best_by_document.get(source_id)
            if current is None or candidate["distance"] < current["distance"]:
                best_by_document[source_id] = candidate

        results = sorted(best_by_document.values(), key=lambda item: item["distance"])[:top_k]
        return results

    def retrieve_by_category(self, category: str) -> List[dict]:
        """Recupera todos os documentos de uma categoria específica."""
        try:
            results = self.collection.get(
                where={"category": category}
            )

            docs = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if results["metadatas"] else {}
                    docs.append({
                        "content": doc,
                        "title": metadata.get("title", "Unknown"),
                        "category": metadata.get("category", ""),
                        "relevance_score": 1.0
                    })

            return docs
        except Exception:
            return []

    def get_context(self, query: str, max_tokens: int = 2000) -> dict:
        """
        Gera contexto relevante para o modelo baseado na consulta.

        CORREÇÃO: sempre retorna um dict com as chaves 'context' e 'nr_documents',
        independentemente de encontrar ou não documentos relevantes.

        Args:
            query: texto de consulta
            max_tokens: limite aproximado de tokens no contexto

        Returns:
            dict com 'context' (str) e 'nr_documents' (int)
        """
        retrieved_docs = self.retrieve(query, top_k=1)

        # Retorna dict vazio ao invés de string — evita TypeError em tools.py
        if not retrieved_docs:
            return {"context": "", "nr_documents": 0}

        context_parts = []
        total_chars = 0

        for doc in retrieved_docs:
            if total_chars > max_tokens * 4:  # Aproximação: 1 token ≈ 4 caracteres
                break

            part = f"{doc['title']}\n{doc['content']}\n"
            context_parts.append(part)
            total_chars += len(part)

        return {
            "context": "\n".join(context_parts),
            "nr_documents": len(retrieved_docs)
        }