def get_system_message(context=""):
    if context:
        return f"""You are a helpful assistant with access to specific document knowledge. 
        
Instructions:
1. First, look at the provided document passages to answer the question.
2. If the passages contain relevant information, use it and cite which passage you used.
3. If the passages don't contain enough information, use your general knowledge but state this.
4. Always be clear about your information source.

Here are the relevant passages:
{context}"""
    else:
        return """You are a helpful assistant. Since no relevant information was found in the documents, 
please answer based on your general knowledge and make it clear that you're doing so."""

def format_context(search_results):
    if not search_results:
        return ""
        
    context = "Here are the relevant passages from the documents:\n\n"
    for idx, result in enumerate(search_results, 1):
        context += f"[Passage {idx}]:\n{result['content']}\n\n"
    return context
