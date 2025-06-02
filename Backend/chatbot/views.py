from django.http import JsonResponse
from chatbot.models import QAEntry, Subject
from random import sample
from django.views.decorators.csrf import csrf_exempt
import re

@csrf_exempt
def generate_quiz(request):
    subject_id = request.GET.get("subject_id")
    broj_pitanja = int(request.GET.get("n", 12))

    if not subject_id:
        return JsonResponse({"error": "subject_id je obavezan."}, status=400)

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return JsonResponse({"error": "Subject ne postoji."}, status=404)

    pitanja = list(QAEntry.objects.filter(subject=subject))

    if len(pitanja) < broj_pitanja:
        return JsonResponse({"error": "Nema dovoljno pitanja za kviz."}, status=400)

    odabrana = sample(pitanja, broj_pitanja)

    # 🔧 Pametno kraćenje
    def skrati_na_recenice(tekst):
        tekst = tekst.strip()
        if not tekst:
            return ""

        # Ako su natuknice, pokušaj uzeti prvu ili dvije
        natuknice = re.split(r'[\n•\-–●]', tekst)
        natuknice = [n.strip() for n in natuknice if n.strip()]
        if len(natuknice) > 0:
            prva = natuknice[0]
            if len(prva) > 200:
                return prva[:200] + "..."
            elif len(natuknice) > 1:
                kombinirano = f"{prva}; {natuknice[1]}"
                return kombinirano if len(kombinirano) <= 220 else prva
            return prva

        # Inače klasično rečenice
        recenice = re.split(r'(?<=[.!?])\s+', tekst)
        prva = recenice[0]
        if len(prva) >= 200 or len(recenice) == 1:
            return prva
        druga = recenice[1] if len(recenice) > 1 else ""
        kombinirano = f"{prva} {druga}".strip()
        return kombinirano if len(kombinirano) <= 220 else prva

    kviz = []

    for entry in odabrana:
        tocan = entry.answer.strip()

        svi_odgovori = list(QAEntry.objects.filter(subject=subject).exclude(id=entry.id).values_list("answer", flat=True))
        netocni = sample(svi_odgovori, 3) if len(svi_odgovori) >= 3 else svi_odgovori

        opcije = sample([tocan] + netocni, len(netocni) + 1)

        kviz.append({
            "pitanje": skrati_na_recenice(entry.question),
            "puno_pitanje": entry.question,
            "opcije": [skrati_na_recenice(o) for o in opcije],
            "tocan": skrati_na_recenice(tocan),
            "predavanje": subject.name
        })
    return JsonResponse({"kviz": kviz}) 