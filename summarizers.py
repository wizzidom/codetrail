async def generate_function_summary_batch(function_sources: list[str]) -> list[str]:
    # I'm creating a single prompt that includes all function sources
    # so I can get summaries for all of them in one request.
    prompt = "Summarize each of these Python functions in one sentence each:\n\n"
    for i, src in enumerate(function_sources, 1):
        prompt += f"Function {i}:\n{src}\n\n"

    # Depending on the model provider, I call the appropriate API.
    if MODE == "ollama":
        response = ollama.chat(
            model='phi',
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['message']['content'].strip()
    else:
        # For now, if I’m not using ollama, I return a placeholder.
        content = "Batch summarization not implemented for this backend."

    # The model should return summaries separated by lines.
    # I parse each line to extract the summary, removing any leading "Function X:" text.
    summaries = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            _, summary = line.split(':', 1)
            summaries.append(summary.strip())
        else:
            summaries.append(line)
    return summaries
