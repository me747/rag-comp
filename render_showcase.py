# turns compression_showcase.json into a simple html page to eyeball, kept sentences shown in green, dropped ones struck through

import json
import sys
import html

def render(showcase_path, output_path="compression_showcase.html"):
    with open(showcase_path) as f:
        data = json.load(f)

    body_parts = []

    for entry in data:
        question = entry["question"]
        body_parts.append(f"<h2>{html.escape(question)}</h2>")

        for i, chunk_data in enumerate(entry["chunks"]):
            kept = chunk_data["kept"]
            dropped = chunk_data["dropped"]

            body_parts.append(f"<p><b>chunk {i+1}</b></p>")

            for s in kept:
                body_parts.append(f'<span style="color: green;">{html.escape(s)}</span> ')

            for s in dropped:
                body_parts.append(f'<span style="text-decoration: line-through; color: gray;">{html.escape(s)}</span> ')

            body_parts.append("<hr>")

    full_html = f"""
<html>
<body>
<h1>compression showcase</h1>
{"".join(body_parts)}
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"saved to {output_path}")

if __name__ == "__main__":
    render(sys.argv[1])