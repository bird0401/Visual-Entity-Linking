import os
import openai
openai.api_key = "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"
# openai.api_key = os.getenv("OPENAI_API_KEY")

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "You are a helpful assistant."},
        {"role": "system", "content": "Hello!"}
    ]
)

# print(completion.choices[0].message)
print(completion.choices)
