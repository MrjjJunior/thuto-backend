
def generate_answer(question, context):
    prompt = f"""
    Use the context below to answer the question

    Context:
    {context}

    Question:
    {question}
    """
    return "Generated answer"