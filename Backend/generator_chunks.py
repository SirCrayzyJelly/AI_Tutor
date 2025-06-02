import json
import re
import os

def split_question(q):
    parts = re.split(r'[.,;]| i | te | odnosno | kako | od čega', q.lower())
    parts = [p.strip() for p in parts if len(p.strip()) > 5]
    return parts

def generate_chunks():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    input_json = os.path.join(base_dir, "initial_data.json")
    output_json = os.path.join(base_dir, "initial_chunks.json")

    with open(input_json, "r", encoding="utf-8") as f:
        raw_entries = json.load(f)

    new_data = []

    for entry in raw_entries:
        question = entry["fields"].get("question", "")
        answer = entry["fields"].get("answer", "")
        link = entry["fields"].get("link")

        chunks = split_question(question)
        chunks.append(question.lower().strip())  # Dodaj cijelo pitanje kao chunk

        for chunk in chunks:
            new_data.append({
                "original": question,
                "chunk": chunk,
                "answer": answer,
                "link": link
            })

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"Spremljeno {len(new_data)} chunkova u {output_json}")


if __name__ == "__main__":
    generate_chunks()
