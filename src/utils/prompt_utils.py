from datetime import datetime

PROMPT_LIMIT = 3750

def chunk_text(text, chunk_size=100):

    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
  
    for sentence in sentences:

        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '. '

    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def build_prompt(query, context_chunks):

    prompt_start = (
        "Answer the question based on the context below. If you don't know the answer based on the context provided below, just respond with 'Hiện tại tôi chỉ hỗ trợ về lĩnh vực ngân hàng của HDBank, vui lòng đặt câu hỏi có liên quan.' instead of making up an answer. Don't start your response with the word 'Answer:'"
        "Context:\n"
    )

    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )

    prompt = ""
  
    for i in range(1, len(context_chunks)):
        if len("\n\n---\n\n".join(context_chunks[:i])) >= PROMPT_LIMIT:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(context_chunks[:i-1]) +
                prompt_end
            )
            break
        elif i == len(context_chunks)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(context_chunks) +
                prompt_end
            )

    return prompt

def construct_messages_list(chat_history, prompt):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for message in chat_history:
        if isinstance(message, dict) and 'isBot' in message:
            if message['isBot']:
                messages.append({"role": "system", "content": message["text"]})
            else:
                messages.append({"role": "user", "content": message["text"]})
        else:
            messages.append({"role": "user", "content": message})
    messages[-1]["content"] = prompt

    return messages


def format_response(data=None, success=True, message="Success"):
    current_time = datetime.now().isoformat()
    response_message = "Success" if success else "Error"
    if message:
        response_message = message
        
    return {
        "responseTime": current_time,
        "responseMessage": response_message,
        "data": data if data else {}
    }