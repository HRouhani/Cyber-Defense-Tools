#!/usr/bin/env python3
"""Optional merge of our synthetic tiny LoRA adapter into base model (no upload)."""
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

ROOT=Path(__file__).resolve().parents[1]/'workspace'/'models'
BASE='sshleifer/tiny-gpt2'
ADAPTER=ROOT/'tiny_lora_adapter'
OUT=ROOT/'tiny_merged'
if not ADAPTER.exists(): raise SystemExit('Run optional_lora_tiny.py first')
base=AutoModelForCausalLM.from_pretrained(BASE)
combined=PeftModel.from_pretrained(base,str(ADAPTER)).merge_and_unload()
OUT.mkdir(parents=True,exist_ok=True)
combined.save_pretrained(str(OUT),safe_serialization=True)
AutoTokenizer.from_pretrained(BASE).save_pretrained(str(OUT))
print('Merged model saved locally:',OUT)
