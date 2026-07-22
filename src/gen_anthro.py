import anthropic
from dotenv import load_dotenv


load_dotenv()
client = anthropic.Anthropic()

def gen_answer(question, context_chunks, model="claude-sonnet-4-6"):

    context = "\n\n***\n\n".join(context_chunks) # joining the context chunks but creating some separation so its clear for the LLM that they are different pieces
    prompt = f"""Answer the question using ONLY the context provided below. If the answer isn't in the context, say "I don't know based on the provided context."

Context:
{context}

Question: {question}

Answer:"""
# not sure if 500 tokens is going to be appro. (might bump up or down)
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    ans_txt = response.content[0].text

    # getting token usage for cost comparison later
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    return {
        "answer": ans_txt,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }

# quick test before using the real retriever
if __name__ == "__main__":
    test_context = ["The standard Part B premium is 2 bananas per month in 2026"] # obv fake context for testing
    question = "What is the premium for Part B"

    result = gen_answer(question, test_context)
    print(result["answer"])
    print(f"tokens used: Before: {result['input_tokens']}, After: {result['output_tokens']}")