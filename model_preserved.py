from transformers import AutoTokenizer, AutoModelForCausalLM,MarianMTModel, MarianTokenizer
# Qwen3-0.6B模型保存
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B")
save_path = "./Qwen3-0.6B"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
# --------- 英文 → 中文模型保存 ---------
en2zh_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-zh")
en2zh_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-zh")

en2zh_tokenizer.save_pretrained("./marianmt_en2zh")
en2zh_model.save_pretrained("./marianmt_en2zh")

# --------- 中文 → 英文模型保存 ---------
zh2en_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
zh2en_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-zh-en")

zh2en_tokenizer.save_pretrained("./marianmt_zh2en")
zh2en_model.save_pretrained("./marianmt_zh2en")

