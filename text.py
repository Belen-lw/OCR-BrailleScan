from transformers import AutoModelForCausalLM, AutoTokenizer # instalar
import torch #instalar

# Carga un modelo preentrenado y su tokenizador
model_name = "gpt2"  # Puedes utilizar otros modelos, como "bert-base-uncased" para tareas de corrección de ortografía
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Texto con error ortográfico
input_text = "Tengo un gato blanc"

# Tokeniza el texto
input_ids = tokenizer.encode(input_text, return_tensors="pt")

# Genera predicciones de palabras para completar la oración
with torch.no_grad():
    output = model.generate(input_ids, max_length=20, num_return_sequences=5, no_repeat_ngram_size=2)

# Decodifica las predicciones
for prediction in output:
    corrected_text = tokenizer.decode(prediction, skip_special_tokens=True)
    print(corrected_text)
