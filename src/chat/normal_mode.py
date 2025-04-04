def get_system_message(context=""):
    if context:
        return f"""You are a helpful assistant with access to specific document knowledge from the Python Parallel Programming Cookbook.

Instructions:
1. **Always start by reviewing the provided document passages before using your general knowledge.**
2. If the passages contain specific instructions or code examples, use them and clearly cite which passage(s) you used.
3. Only if the passages do not contain enough information, supplement your answer using your general knowledge—and state when you do.
4. Always be clear about your information source.
5. **When providing any code, please wrap it in triple backticks (e.g., ```python ... ```) so it displays as a properly formatted code block.**

Here are the relevant passages:
{context}"""
    else:
        return """You are a helpful assistant. Since no relevant information was found in the documents,
please answer based on your general knowledge and make it clear that you're doing so.
When providing any code, please wrap it in triple backticks (e.g., ```python ... ```) so it displays as a properly formatted code block."""



def format_context(search_results):
    if not search_results:
        return ""
        
    context = "Here are the relevant passages from the documents:\n\n"
    for idx, result in enumerate(search_results, 1):
        context += f"[Passage {idx}]:\n{result['content']}\n\n"
    return context
