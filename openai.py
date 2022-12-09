import openai

openai.api_key = "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"

prompt = "What is the capital of France?"

completions = openai.Completion.create(
  engine="text-davinci-002",
  prompt=prompt,
  max_tokens=128,
  n=1,
  stop=None,
  temperature=0.5,
)

print(completions.choices[0].text)
