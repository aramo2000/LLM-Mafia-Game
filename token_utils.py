import tiktoken


def count_openai_input_tokens(messages, model="gpt-4o-2024-08-06"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("didn't find model. Using the default")
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = 3
    tokens_per_name = 1
    total_tokens = 0

    for msg in messages:
        total_tokens += tokens_per_message
        for key, value in msg.items():
            total_tokens += len(encoding.encode(value))
            if key == "name":
                total_tokens += tokens_per_name

    total_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return total_tokens


def count_openai_output_tokens(text, model="gpt-4o-2024-08-06"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
