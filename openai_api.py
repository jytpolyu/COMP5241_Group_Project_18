import openai

openai.api_key = 'your-openai-api-key'

def generate_summary(data):
    prompt = f"Analyze the following student performance data: {data}"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
    return response.choices[0].text.strip()
