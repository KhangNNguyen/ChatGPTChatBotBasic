import aitest

def handle_response(message) -> str:
    context_file = "prompt.txt"
    context_message = aitest.load_context_from_file(context_file)
    response = aitest.chat_with_gpt(message, context_message)
    return response
