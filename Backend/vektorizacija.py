import os
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Dinamičko određivanje putanja
base_dir = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(base_dir, "initial_chunks.json")  # Koristimo chunkove!
faiss_index_path = os.path.join(base_dir, "faiss.index")
embeddings_file_path = os.path.join(base_dir, "all_vectors.txt")

class QABase:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.data = []

    def load_data(self, json_path=json_path, force_rebuild=False):
        if force_rebuild:
            if os.path.exists(faiss_index_path):
                os.remove(faiss_index_path)
            if os.path.exists(embeddings_file_path):
                os.remove(embeddings_file_path)

        print(f"Učitavam podatke iz: {json_path}")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_entries = json.load(f)

            print(f"Broj pitanja učitanih (chunkova): {len(raw_entries)}")

            self.data = []
            all_chunks = []

            for entry in raw_entries:
                chunk = entry.get("chunk", "")
                answer = entry.get("answer", "")
                link = entry.get("link")
                self.data.append({
                    "chunk": chunk,
                    "answer": answer,
                    "link": link
                })
                all_chunks.append(chunk)

            if os.path.exists(faiss_index_path) and os.path.exists(embeddings_file_path):
                print(f"✅ Učitavam postojeći FAISS indeks iz {faiss_index_path}")
                self.index = faiss.read_index(faiss_index_path)
            else:
                print(f"⚙️ Generiram embeddinge i FAISS indeks...")
                embeddings = self.model.encode(all_chunks, convert_to_numpy=True, normalize_embeddings=True)

                with open(embeddings_file_path, "w", encoding="utf-8") as f:
                    for emb in embeddings:
                        f.write(' '.join(map(str, emb)) + "\n")

                self.index = faiss.IndexFlatIP(embeddings.shape[1])
                self.index.add(embeddings)
                faiss.write_index(self.index, faiss_index_path)
                print(f"💾 FAISS indeks spremljen u {faiss_index_path}")

        except FileNotFoundError:
            print(f"❌ Datoteka nije pronađena: {json_path}")
        except Exception as e:
            print(f"⚠️ Pogreška: {e}")

    def search(self, query, top_k=5, threshold=0.65, api_fallback=None):
        if not self.index or not self.data:
            return None

        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(query_embedding, top_k)

        print(f"🔍 Sličnosti rezultata: {D[0]}")  # Debug ispis za provjeru rezultata

        for i in range(top_k):
            if D[0][i] >= threshold:
                result = self.data[I[0][i]]
                response_text = f"(Odgovor iz baze)\n\n{result['answer']}"
                if result.get("link"):
                    response_text += f"\n\n🔗 [Više informacija]({result['link']})"
                return response_text
        print("Nema odgovora iz baze - vracam API")
        return None  # Nema dovoljno sličnog odgovora

if __name__ == "__main__":
    qa_base = QABase()
    qa_base.load_data(force_rebuild=True)
