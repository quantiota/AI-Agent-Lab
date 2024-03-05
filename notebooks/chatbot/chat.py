from openai import OpenAI
import os

API_KEY = os.environ.get('OPENAI_API_KEY')
if API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=API_KEY)
history = []

def ask(question):
    history.append({"role": "user", "content": question})
    response = client.chat.completions.create(messages=history, model="gpt-3.5-turbo")
    history.append(response.choices[0].message)
    return response.choices[0].message.content

while True:
    question = input("User: ")
    if not question.strip():
        break
    answer = ask(question)
    print("\nAI:", answer, "\n")