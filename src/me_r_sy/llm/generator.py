import json

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen3-4B-Instruct-2507"


class MeteorologicalReportGenerator:

    def __init__(self):
        print(f"Loading model: {MODEL_NAME}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype="auto",
            device_map="auto",
        )

        self.model.eval()

    def generate(self, data: dict) -> str:

        json_data = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )

        prompt = f"""
You are a professional meteorologist working for a meteorological service.

Your task is to transform verified meteorological statistics into a
scientifically accurate monthly meteorological report.

IMPORTANT RULES:

1. Do not invent numerical values.
2. Use only the information provided in the JSON.
3. Do not perform calculations unless absolutely necessary.
4. Clearly distinguish observations from interpretations.
5. Use professional meteorological terminology.
6. Write the report in French.
7. Produce a clear and concise report.
8. If information is missing, do not invent it.

Meteorological data:

{json_data}

Write the meteorological report now.
"""

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert meteorologist and scientific "
                    "report writer."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1500,
                temperature=0.3,
                do_sample=True,
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

        report = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        )

        return report
