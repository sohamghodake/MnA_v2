import ollama

response = ollama.chat(
    model="qwen3:80b-cloud",
    messages=[
        {"role": "system", "content": "You are an M&A analyst."},
        {"role": "user", "content": "List 3 compounding M&A risks."}
    ]
)

print(response["message"]["content"])
    