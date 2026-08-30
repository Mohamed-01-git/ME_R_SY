import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import numpy as np


class LLM:

    def __init__(self, daily_stats, anomaly, year, month):
        self.daily_stats = daily_stats
        self.anomaly = anomaly
        self.year = year
        self.month = month

    def create_items(self, ds, stat):
        out = {}
        for var in ds:
            out[var] = {
                "lon": float(ds[var]["lon"].item()),
                "lat": float(ds[var]["lat"].item()),
                "values": float(ds[var]["values"].reduce(stat).values),
                "day": str(ds[var]["day"].values),
            }
        return out

    def create_message(self):
        message = {
            "studied_period": {"year": int(self.year), "month": int(self.month)},
            "reference_period": {"start_year": 1991, "end_year": 2020},
            # "monthly": self.create_items(self.statistics["mean"], np.max),
            "max": self.create_items(self.daily_stats["max"], np.max),
            "min": self.create_items(self.daily_stats["min"], np.min),
            "anomaly": {
                name: float(var.values.mean()) for name, var in self.anomaly.items()
            },
        }
        return json.dumps(message, indent=4, ensure_ascii=False)


import json
import requests


class ReportGenerator:

    def __init__(
        self,
        url="http://127.0.0.1:8081/v1/chat/completions",
        model="lmstudio-community/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M",
    ):
        self.url = url
        self.model = model

    def _generate(self, prompt, max_tokens=150):

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Tu es un météorologue expert "
                            "spécialisé dans l'analyse "
                            "météorologique du Maroc."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.2,
                "max_tokens": max_tokens,
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    # ---------------------------------------------------------
    # Temperature
    # ---------------------------------------------------------

    def generate_max(self, data):

        prompt = f"""
Rédige uniquement le commentaire de la section
"MAXIMUMS" d'un rapport météorologique mensuel.

Données météorologiques :

{json.dumps(data, ensure_ascii=False, indent=2)}

Le commentaire doit :

- présenter les maximums des différentes variables météorologiques ;
- mentionner les dates et localisations disponibles ;
- interpréter correctement les maximums ;
- rester factuel ;
- ne rien inventer.

N'inclus aucun titre.
Ne mentionne pas le JSON, les instructions ou le prompt.

Rédige uniquement le commentaire météorologique.
"""

        return self._generate(prompt, max_tokens=150)

    # ---------------------------------------------------------
    # MINIMUMS
    # ---------------------------------------------------------
    def generate_min(self, data):

        prompt = f"""
Rédige uniquement le commentaire de la section
"MINIMUMS" d'un rapport météorologique mensuel.

Données météorologiques :

{json.dumps(data, ensure_ascii=False, indent=2)}

Le commentaire doit :

- présenter les minimums des différentes variables météorologiques ;
- mentionner les dates et localisations disponibles ;
- interpréter correctement les minimums ;
- rester factuel ;
- ne rien inventer.

N'inclus aucun titre.
Ne mentionne pas le JSON, les instructions ou le prompt.

Rédige uniquement le commentaire météorologique.
"""

        return self._generate(prompt, max_tokens=150)

    def generate_anomaly(self, data):

        prompt = f"""
Rédige uniquement le commentaire de la section
"Anomalie" d'un rapport météorologique mensuel.

Données météorologiques :

{json.dumps(data, ensure_ascii=False, indent=2)}

Le commentaire doit :
- analyser l'anomalie par rapport à 1991-2020 ;
- mentionner les dates et localisations disponibles ;
- ne pas tirer de conclusion non justifiée par les données ;
- rester factuel ;
- ne rien inventer.

N'inclus aucun titre.
Ne mentionne pas le JSON, les instructions ou le prompt.

Rédige uniquement le commentaire météorologique.
"""

        return self._generate(prompt, max_tokens=150)

    # ---------------------------------------------------------
    # Pressure
    # ---------------------------------------------------------

    def generate_monthly(self, data):

        prompt = f"""
Rédige uniquement le commentaire de la section
"moyenne mensuelle" d'un rapport météorologique mensuel.

Données météorologiques :

{json.dumps(data, ensure_ascii=False, indent=2)}

Le commentaire doit :

- présenter les valeurs des differentes variables disponibles ;
- mentionner les dates et localisations disponibles ;
- rester factuel ;
- ne rien inventer.

N'inclus aucun titre.
Ne mentionne pas le JSON, les instructions ou le prompt.

Rédige uniquement le commentaire météorologique.
"""

        return self._generate(prompt, max_tokens=120)

    # ---------------------------------------------------------
    # General summary
    # ---------------------------------------------------------

    def generate_summary(self, sections):

        prompt = f"""
Rédige une synthèse générale courte pour un rapport
météorologique mensuel sur le Maroc.

Commentaires des différentes sections :

{json.dumps(sections, ensure_ascii=False, indent=2)}

La synthèse doit :

- présenter les principaux faits météorologiques du mois ;
- mettre en évidence les anomalies importantes ;
- éviter de répéter inutilement toutes les valeurs ;
- rester cohérente avec les sections ;
- ne rien inventer.

N'inclus aucun titre.
Ne mentionne pas le JSON, les instructions ou le prompt.

Rédige uniquement la synthèse météorologique.
"""

        return self._generate(prompt, max_tokens=180)

    # ---------------------------------------------------------
    # Complete report
    # ---------------------------------------------------------

    def generate_report(self, message):

        sections = {}

        sections["anomaly"] = self.generate_anomaly(message)

        sections["monthly"] = self.generate_monthly(message)

        sections["max"] = self.generate_max(message)

        sections["min"] = self.generate_min(message)

        sections["summary"] = self.generate_summary(sections)

        return sections
