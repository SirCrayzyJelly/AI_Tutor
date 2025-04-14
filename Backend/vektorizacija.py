import os
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Dinamičko određivanje ispravne putanje
base_dir = os.path.dirname(os.path.realpath(__file__))  # Putanja do trenutne Python datoteke
json_path = os.path.join(base_dir, "initial_data.json")  # Ispravna putanja do JSON datoteke

# Definicija klase za upravljanje pitanjima i odgovorima
class QABase:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.data = []

    def load_data(self, json_path=json_path):
        # Provjera postoji li JSON datoteka
        print(f"Učitavam podatke iz: {json_path}")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_entries = json.load(f)

            print(f"Broj pitanja učitanih: {len(raw_entries)}")

            # Ispisivanje cijelog unosa kako bismo provjerili strukturu
            print(f"Primjer jednog unosa:")
            print(raw_entries[3])  # Prilagodit ćemo za unos koji sadrži 'question' (koji je četvrti u ovom primjeru)

            # Provjera i ekstrakcija pitanja
            self.data = []
            for entry in raw_entries:
                if "question" in entry["fields"]:
                    self.data.append(entry["fields"])  # Dodajemo samo one koji sadrže "question"
                else:
                    print(f"Unos bez pitanja: {entry['pk']}")

            questions = [item["question"] for item in self.data]  # Ovdje pristupamo 'question' unutar 'fields'

            # Provjera da li već postoji spremljena datoteka s vektorima
            embeddings_file_path = os.path.join(base_dir, "all_vectors.txt")
            if os.path.exists(embeddings_file_path):
                print(f"{embeddings_file_path} već postoji. Preskačemo vektorizaciju.")
                # Učitavanje vektora iz tekstualne datoteke
                with open(embeddings_file_path, "r", encoding="utf-8") as f:
                    embeddings = np.loadtxt(f)
            else:
                # Ako datoteka ne postoji, generiramo vektore
                print(f"{embeddings_file_path} ne postoji. Generiramo nove vektore.")
                # Vektorizacija pitanja
                embeddings = self.model.encode(questions, convert_to_numpy=True, normalize_embeddings=True)
                print(f"Oblik vektora: {embeddings.shape}")

                # Ispisivanje vektora za svako pitanje
                for i, question in enumerate(questions):
                    print(f"Vektor za pitanje '{question}':")
                    print(embeddings[i])

                # Spremanje vektora u tekstualnu datoteku
                print(f"Spremam vektore u: {embeddings_file_path}")
                with open(embeddings_file_path, "w", encoding="utf-8") as f:
                    for emb in embeddings:
                        f.write(' '.join(map(str, emb)) + "\n")

            # Kreiranje FAISS indeksa
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)

        except FileNotFoundError:
            print(f"Datoteka nije pronađena na putanji: {json_path}")
        except Exception as e:
            print(f"Došlo je do pogreške: {e}")

    def search(self, query, top_k=1, threshold=0.75):
        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(query_embedding, top_k)
        if D[0][0] >= threshold:
            result = self.data[I[0][0]]
            response_text = f"(Odgovor iz baze)\n\n{result['answer']}"
            if result.get("link"):
                response_text += f"\n\n🔗 [Više informacija]({result['link']})"
            return response_text
        else:
            return None

# Pokretanje učitavanja podataka i vektorizacije
qa_base = QABase()
qa_base.load_data()
