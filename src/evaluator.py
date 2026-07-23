# instead of manually checking if the generated ans matches the expected (ans be worded differently but still be correct)
# using LLM as a judge for this

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def judge_ans(question, expected_ans, uncompressed_ans,compressed_ans, model="claude-sonnet-4-6"): # should have used haiku for eval, lowk forgot .-.
    # asking a different LLM to grade the answer, I'm not sure how reliable this is
    prompt = f"""You are grading whether a generated answer is factually correct compared to an expected answer.

Question: {question}
Expected answer: {expected_ans}

Answer A: {uncompressed_ans}
Answer B: {compressed_ans}

Is the generated answer factually consistent with the expected answer? Ignore differences in wording or phrasing - only care about factual correctness.

Respond in exactly this format, nothing else:
A: CORRECT/PARTIALLY_CORRECT/INCORRECT
B: CORRECT/PARTIALLY_CORRECT/INCORRECT"""

    response = client.messages.create(
        model=model,
        max_tokens=30, # *ughh bumping from 20->30 lost like 9 cents(a cheap lesson considerably) on truncation causing a crash
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    lines = [l for l in raw.split("\n") if l.strip()] # *parsing the 2 line response into separate verdicts
    verdict_a = lines[0].replace("A:", "").strip() if len(lines) > 0 else "UNKNOWN" # *making sure parsing doesn't crash like the first test-run
    verdict_b = lines[1].replace("B:", "").strip() if len(lines) > 1 else "UNKNOWN"

    return verdict_a, verdict_b

def score_verdict(verdict):
    # turning verdict into a numerical value to avg.
    if verdict == "CORRECT":
        return 1.0
    elif verdict == "PARTIALLY_CORRECT":
        return 0.5
    else:
        return 0.0

if __name__ == "__main__":

    que = "What is the Part B premium?"
    expected = "The standard Part B premium is 2 bananas per month in 2026"
    uncompressed_answer = "It costs 2 bananas monthly for standard Part B premium."
    compressed_answer = "2 bananas"

    verdict_a, verdict_b = judge_ans(que, expected, uncompressed_answer, compressed_answer)
    print(f"uncompressed verdict: {verdict_a}")
    print(f"compressed verdict: {verdict_b}")