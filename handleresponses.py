import aitest

def handle_response(message) -> str:
    context_file = "prompt.txt"
    context_message = aitest.load_context_from_file(context_file)
    response = aitest.chat_with_gpt(message, context_message)
    if len(response) > 2000:
        out = [(response[i:i+1900]) for i in range (0,len(response), 1900)]
        return out
        #return ("The response is greater than 2000 characters (discord limit) please revise your prompt to limit the response to under 2000 characters. :nerd: ")
    else:
        out = [response]
        return out
