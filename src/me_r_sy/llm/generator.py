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
            print(f"\nVariable: {var}")

            for name in ["lon", "lat", "values", "day"]:
                if name in ds[var]:
                    arr = ds[var][name]
                    print(
                        f"{name}: type={type(arr).__name__}, "
                        f"shape={getattr(arr, 'shape', None)}"
                    )
            out[var] = {
                "lon": float(ds[var]["lon"]),
                "lat": float(ds[var]["lat"]),
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


import requests
import json
from google import genai


class ReportGenerator:

    def __init__(self, model="gemini-3.5-flash-lite"):
        self.client = genai.Client()
        self.model = model

    def _generate(self, prompt, max_tokens=150):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "system_instruction": (
                    "Tu es un météorologue expert spécialisé "
                    "dans l'analyse météorologique du Maroc. "
                    "Tu produis des commentaires météorologiques "
                    "factuels, précis et professionnels en français. "
                    "Tu ne dois jamais inventer de données."
                ),
                "temperature": 0.2,
                "max_output_tokens": max_tokens,
            },
        )
        print("RESPONSE \n")
        print(response)

        print("RESPONSE TXT \n")
        print(response.text)

        return response.text.strip()

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

    def generate_report(self, message, year, month):

        report = rf"""
\documentclass[a4paper,12pt]{{article}}

\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{graphicx}}
\usepackage{{float}}
\usepackage{{geometry}}

\geometry{{margin=2.5cm}}

\begin{{document}}

% =========================================================
% TITLE PAGE
% =========================================================

\begin{{titlepage}}

\newgeometry{{top=1.5cm,bottom=1.5cm,left=2cm,right=2cm}}

\begin{{center}}

\vspace*{{0.5cm}}

{{\Large\textbf{{ME-R-SY}}}}

\vspace{{0.1cm}}

{{\small\textit{{Meteorological Reporting System}}}}

\vspace{{0.8cm}}

\noindent\rule{{0.85\textwidth}}{{1.2pt}}

\vspace{{1.0cm}}

{{\Huge\textbf{{Rapport météorologique mensuel}}}}

\vspace{{0.3cm}}

{{\Large
Analyse des conditions météorologiques\\
et des anomalies climatiques
}}

\vspace{{0.8cm}}

% =========================================================
% MAIN FIGURE
% =========================================================

\includegraphics[
    width=0.82\textwidth,
    height=7cm,
    keepaspectratio
]{{figures/mean\_{year}\_{month:02d}.png}}

\vspace{{0.3cm}}

{{\small\textit{{Distribution spatiale des conditions météorologiques
au Maroc}}}}

\vspace{{0.8cm}}

% =========================================================
% PERIOD
% =========================================================

\fbox{{%
\begin{{minipage}}{{0.55\textwidth}}
\centering
\vspace{{0.25cm}}

{{\large\textbf{{Période étudiée}}}}

\vspace{{0.1cm}}

{{\LARGE\textbf{{{month:02d} / {year}}}}}

\vspace{{0.15cm}}

{{\small Référence climatique : 1991--2020}}

\vspace{{0.25cm}}
\end{{minipage}}
}}

\vfill

% =========================================================
% DESCRIPTION
% =========================================================

\begin{{minipage}}{{0.80\textwidth}}
\centering
\small
Rapport généré automatiquement à partir des données
météorologiques et des analyses statistiques du système ME-R-SY.
\end{{minipage}}

\vspace{{0.8cm}}

\noindent\rule{{0.85\textwidth}}{{0.6pt}}

\vspace{{0.25cm}}

{{\small
\textbf{{ME-R-SY}}
\quad | \quad
Meteorological Data Analysis
\quad | \quad
Automated Reporting
}}

\end{{center}}

\restoregeometry

\end{{titlepage}}


\section{{Synthèse générale}}

{self.generate_anomaly(message)}

\begin{{figure}}[H]
    \centering
    \includegraphics[width=\textwidth]{{figures/mean_{year}_{month:02d}.png}}
    \caption{{Moyennes météorologiques}}
\end{{figure}}

\section{{Conditions mensuelles}}

{self.generate_monthly(message)}

\section{{Maximums}}

{self.generate_max(message)}

\begin{{figure}}[H]
    \centering
    \includegraphics[width=\textwidth]{{figures/max_{year}_{month:02d}.png}}
    \caption{{Valeurs maximales}}
\end{{figure}}

\section{{Minimums}}

{self.generate_min(message)}

\begin{{figure}}[H]
    \centering
    \includegraphics[width=\textwidth]{{figures/min_{year}_{month:02d}.png}}
    \caption{{Valeurs minimales}}
\end{{figure}}

\section{{Anomalies}}

{self.generate_anomaly(message)}

\begin{{figure}}[H]
    \centering
    \includegraphics[width=\textwidth]{{figures/anom_{year}_{month:02d}.png}}
    \caption{{Anomalies météorologiques}}
\end{{figure}}

\end{{document}}
"""

        return report
