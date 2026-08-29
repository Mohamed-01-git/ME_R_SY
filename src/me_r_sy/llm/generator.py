import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LLM:

    def __init__(self, daily_stats, anomaly, year, month):
        self.daily_stats = daily_stats
        self.anomaly = anomaly
        self.year = year
        self.month = month

    def create_items(self, var):
        out = {
            "maximum": {
                "value": float(self.daily_stats["max"][var]["values"].max().values),
                "day": str(self.daily_stats["max"][var]["day"].values),
                "latitude": float(self.daily_stats["max"][var]["lat"].item()),
                "longitude": float(self.daily_stats["max"][var]["lon"].item()),
            },
            "minimum": {
                "value": float(self.daily_stats["min"][var]["values"].min().values),
                "day": str(self.daily_stats["min"][var]["day"].values),
                "latitude": float(self.daily_stats["min"][var]["lat"].item()),
                "longitude": float(self.daily_stats["min"][var]["lon"].item()),
            },
            "anomaly": float(self.anomaly[var].mean().values),
        }

        return out

    def create_message(self):

        message = {
            "studied_period": {"year": int(self.year), "month": int(self.month)},
            "reference_period": {"start_year": 1991, "end_year": 2020},
            "temperature": self.create_items("t2m"),
            "pressure": self.create_items("msl"),
            "wind": self.create_items("w"),
            "precipitations": {
                "maximum": {
                    "value": float(
                        self.daily_stats["max"]["tp"]["values"].min().values
                    ),
                    "day": str(self.daily_stats["max"]["tp"]["day"].values),
                    "latitude": float(self.daily_stats["max"]["tp"]["lat"].item()),
                    "longitude": float(self.daily_stats["max"]["tp"]["lon"].item()),
                },
                "anomaly": float(self.anomaly["tp"].mean().values),
            },
        }
        return message

    def to_json(self):
        message = self.create_message()
        json_msg = json.dumps(message, indent=4, ensure_ascii=False)
        return json_msg


class ReportGenerator:

    def __init__(self, model_name):

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype="auto", device_map="auto"
        )

    def generate(self, message):

        prompt = f"""
Tu es un météorologue expert spécialisé dans l'analyse
climatique et météorologique du Maroc.

À partir des données météorologiques JSON ci-dessous,
rédige un rapport météorologique mensuel professionnel
en français.

Le rapport doit :

1. Présenter une synthèse générale du mois.
2. Décrire les températures et leurs anomalies.
3. Décrire les précipitations et les événements pluvieux remarquables.
4. Décrire les conditions de pression atmosphérique.
5. Décrire les conditions de vent.
6. Mentionner les valeurs extrêmes lorsqu'elles sont pertinentes.
7. Comparer les conditions du mois à la période de référence 1991-2020.
8. Ne jamais inventer une information absente du JSON.
9. Utiliser uniquement les données fournies.
10. vous aves les lon, lat, determiner la zone géographique au maroc.
10. Employer un style professionnel adapté à un bulletin météorologique.

Données météorologiques :

{message}

Rédige uniquement le rapport météorologique final.
"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1500,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1] :]

        report = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        return report
