from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from core.embedder import load_vectorstore

load_dotenv()

PROMPT_TEMPLATE = """
You are a precise document assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I could not find this in the provided documents."
Always end your answer by listing the source pages you used, like: "Source pages used: Page X, Page Y"

Context:
{context}
"""

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )

def format_history(chat_history: list[dict]) -> list:
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    return messages

def answer_question(
    question: str,
    collection_name: str = "documind",
    chat_history: list[dict] = []
):
    vectorstore = load_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    relevant_chunks = retriever.invoke(question)

    if not relevant_chunks:
        return "No relevant content found in the documents.", []

    context = "\n\n---\n\n".join([
        f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}"
        for doc in relevant_chunks
    ])

    sources = list(set([
        f"Page {doc.metadata.get('page', '?')}"
        for doc in relevant_chunks
    ]))

    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    llm = get_llm()
    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "history": format_history(chat_history),
        "question": question
    })

    return response.content, sources