from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langgraph.graph import START, END, StateGraph
from langchain_community.chat_models import ChatOllama
from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
import re
# 1. Configuration
from langchain_ollama import ChatOllama, OllamaEmbeddings

# 1. Use Gemma for the 'Thinking' and 'Answering'
llm = ChatOllama(
    model="gemma3:4b",
    base_url="http://ollama:11434",
    temperature=0
)

# 2. Use mxbai-embed-large for the 'Searching' (Vectorstore)
# DO NOT use gemma3 here.
embed = OllamaEmbeddings(
    model="mxbai-embed-large", 
    base_url="http://ollama:11434"
)

# 3. Update your Chroma reference
vectorstore_from_directory = Chroma(
    persist_directory="/app/vectorstore/credit_risk_management_guidebook",
    embedding_function=embed # Use the embed model, not the llm
)

class GraphState(BaseModel):
    user_input: str
    decision: Optional[Literal["สินเชื่อ", "เปิดบัญชีอย่างไร", "ยอดเงินไม่เข้า", "สแกนจ่ายไม่ได้", "unknown","greeting"]] = Field(default=None)
    final_output: Optional[str] = Field(default=None)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

def retrieve_relevant_docs(query: str, threshold: float):

    # 1. Use the method that returns both the Doc and the Score
    # Note: 'k' here is the initial pool to check before filtering
    results_with_scores = vectorstore_from_directory.similarity_search_with_relevance_scores(
        query, 
        k=5
    )

    # 2. Filter based on your threshold
    # results_with_scores is a list of tuples: [(Document, score), ...]
    filtered_docs = [
        doc for doc, score in results_with_scores 
        if score >= threshold
    ]

    return filtered_docs

def validator(state: GraphState):
    """Hybrid Validator: String matching for buttons (0 tokens), LLM for text."""
    user_input = state.user_input.strip().lower()
    # Fast Path: Check if input exactly matches button options
    valid_options = ["สินเชื่อ", "เปิดบัญชีอย่างไร", "ยอดเงินไม่เข้า", "สแกนจ่ายไม่ได้"]
    if user_input in valid_options:
        return {
            "decision": user_input, 
            "raw_metadata": {"method": "string_match", "tokens": 0, "time": datetime.now().isoformat()} 
        }
    
    greetings = ["hi", "hello", "สวัสดี", "หวัดดี", "sawasdee", "hey"]
    if any(greet in user_input for greet in greetings):
        return {"decision": "greeting", "raw_metadata": {"method": "string_match", "tokens": 0}}
    
    return {"decision": "unknown"}

def option1_node(state: GraphState):
    # Topic: สินเชื่อ (Loans)
    return {
        "final_output": "คุณสามารถสมัครสินเชื่อเบื้องต้นได้ผ่านแอปพลิเคชันในเมนู 'สินเชื่อ' หรือติดต่อสาขาใกล้บ้านครับ",
        "raw_metadata": {"method": "static_response", "tokens": 0,
            "timestamp": datetime.now().isoformat()}
    }

def option2_node(state: GraphState):
    # Topic: เปิดบัญชีอย่างไร (How to open an account)
    return {
        "final_output": "การเปิดบัญชีใหม่สามารถทำได้ง่ายๆ ผ่านแอปโดยใช้การยืนยันตัวตนรูปแบบดิจิทัล (NDID) ได้เลยครับ",
        "raw_metadata": {"method": "static_response", "tokens": 0,
            "timestamp": datetime.now().isoformat()}
    }

def option3_node(state: GraphState):
    # Topic: ยอดเงินไม่เข้า (Balance not updated)
    return {
        "final_output": "หากยอดเงินไม่เข้า โปรดรอตรวจสอบระบบ 1-2 ชั่วโมง หรือส่งหลักฐานสลิปให้เจ้าหน้าที่ตรวจสอบผ่านแชทนี้ครับ",
        "raw_metadata": {"method": "static_response", "tokens": 0,
            "timestamp": datetime.now().isoformat()}
    }

def option4_node(state: GraphState):
    # Topic: สแกนจ่ายไม่ได้ (Cannot scan to pay)
    return {
        "final_output": "หากสแกนจ่ายไม่ได้ โปรดตรวจสอบยอดเงินในบัญชี หรือตรวจสอบว่าแอปพลิเคชันเป็นเวอร์ชันล่าสุดแล้วหรือไม่",
        "raw_metadata": {"method": "static_response", "tokens": 0,
            "timestamp": datetime.now().isoformat()}
    }
def greeting_node(state: GraphState):
    user_input = state.user_input.lower()
    
    # 1. Detect language statically (Simple check)
    # If the input contains Thai characters, respond in Thai
    is_thai = bool(re.search(r'[\u0e00-\u0e7f]', user_input))
    
    if is_thai:
        greeting_text = "สวัสดีครับ ผมเป็นผู้ช่วย AI จาก TTB ยินดีที่ได้บริการครับ วันนี้มีอะไรให้ช่วยดูแลไหมครับ?"
    else:
        greeting_text = "Hello! I am your TTB AI Assistant. How can I help you with your banking needs today?"

    # 2. Return with 0 token metadata
    return {
        "final_output": greeting_text,
        "raw_metadata": {
            "method": "static_response",
            "tokens": 0,
            "latency": "0ms",
            "timestamp": datetime.now().isoformat()
        }
    }

# def unknown_node(state: GraphState):
#     """Handles free-text inquiry using the model."""
#     prompt = PromptTemplate.from_template("You are a helpful AI assistant. Answer this: {user_input} in very brief to the point.***used same language as user***")
#     chain = prompt | llm
#     # We MUST pass the user_input here so the model knows what to answer
#     response = chain.invoke({"user_input": state.user_input})
#     return {"final_output": response.content, "raw_metadata": response.response_metadata}


#-------------------------------------------
# def unknown_node(state: GraphState):
#     """Handles free-text inquiry using the model."""
#     prompt = PromptTemplate.from_template("You are a helpful AI assistant. Answer this: {user_input} in very brief to the point.***used same language as user***")
#     chain = prompt | llm
#     # We MUST pass the user_input here so the model knows what to answer
#     response = chain.invoke({"user_input": state.user_input})
#     return {"final_output": response.content, "raw_metadata": response.response_metadata}
#-------------------------------------------

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def unknown_node(state: GraphState):
    """Handles free-text inquiry using RAG with threshold fallback logic."""
    user_input = state.user_input
    th = 0.75
    
    # 1. Try High Threshold (0.75)
    rag_results = retrieve_relevant_docs(user_input, threshold=th)
    # Check if we got results
    if len(rag_results) > 0:
        context_text = rag_results[0].page_content
        template = """You are an AI assistant for TTB bank. Answer the user based ONLY on context.
        Context: {context}
        Question: {question}
        Keep it professional and use the same language as the user."""
        
        prompt = PromptTemplate.from_template(template)
        chain = ({"context": lambda x: context_text, "question": RunnablePassthrough()} 
                 | prompt | llm)
        
        answer = chain.invoke(user_input)
        return {
        "final_output": answer.content,
        "raw_metadata": {
            "method": f"Generated via RAG with high threshold ({answer.response_metadata['model']})",
            "input_tokens": answer.response_metadata['prompt_eval_count'],
            "time_to_read": answer.response_metadata['prompt_eval_duration'],
            "output_tokens": answer.response_metadata['eval_count'],
            "time_to_generate": answer.response_metadata['eval_duration'],
            "timestamp": datetime.now().isoformat()
        
        }}
        # return {"final_output": answer}

    # 2. Try Lower Threshold (0.6)
    low_th = th - 0.15
    rag_results_low = retrieve_relevant_docs(user_input, threshold=low_th)
    
    if len(rag_results_low) > 0:
        #from your infomation we have something like this
        context_text = rag_results_low[0].page_content
        template = """You are an AI assistant for TTB bank. 
        Create a new recommended question by adding on this context.
        Context: {context}
        User Query: {question}
        Keep it concise and use the same language as the user."""
        
        prompt = PromptTemplate.from_template(template)
        chain = ({"context": lambda x: context_text, "question": RunnablePassthrough()} 
                 | prompt | llm )
        
        recommendation = chain.invoke(user_input)
        return {
        "final_output": recommendation.content,
        "raw_metadata": {
            "method": f"Generated recommendation question with acceptable threshold ({recommendation.response_metadata['model']})",
            "input_tokens": recommendation.response_metadata['prompt_eval_count'],
            "time_to_read": recommendation.response_metadata['prompt_eval_duration'],
            "output_tokens": recommendation.response_metadata['eval_count'],
            "time_to_generate": recommendation.response_metadata['eval_duration'],
            "timestamp": datetime.now().isoformat()
        
        }}
        # return {"final_output": recommendation}

    # 3. Default Fallback (No Context Found)
    else:
        fallback_prompt = PromptTemplate.from_template(
            'You are a helpful AI assistant. Say: "I don\'t have that information about {user_input}" '
            'briefly and in the same language as the user.'
        )
        chain = fallback_prompt | llm 
        answer = chain.invoke({"user_input": user_input})
        return {
        "final_output": answer.content,
        "raw_metadata": {
            "method": f"fallback answer with low threshold ({answer.response_metadata['model']})",
            "input_tokens": answer.response_metadata['prompt_eval_count'],
            "time_to_read": answer.response_metadata['prompt_eval_duration'],
            "output_tokens": answer.response_metadata['eval_count'],
            "time_to_generate": answer.response_metadata['eval_duration'],
            "timestamp": datetime.now().isoformat()
        
        }}

# 4. Router Logic
def router(state: GraphState):
    # If it matches one of our Thai buttons, route to specific nodes
    if state.decision in ["สินเชื่อ", "เปิดบัญชีอย่างไร", "ยอดเงินไม่เข้า", "สแกนจ่ายไม่ได้"]:
        # You would need nodes for each of these, or one 'button_handler_node'
        return state.decision
    
    if state.decision == "greeting":
        return "greeting"
    
    return "unknown"

# 5. Graph Construction
builder = StateGraph(GraphState)

builder.add_node("validator", validator)
builder.add_node("option1_node", option1_node)
builder.add_node("option2_node", option2_node)
builder.add_node("option3_node", option3_node)
builder.add_node("option4_node", option4_node)
builder.add_node("unknown_node", unknown_node)
builder.add_node("greeting_node", greeting_node)

builder.add_edge(START, "validator")
builder.add_conditional_edges("validator", router, {
    "สินเชื่อ": "option1_node",
    "เปิดบัญชีอย่างไร": "option2_node",
    "ยอดเงินไม่เข้า": "option3_node",
    "สแกนจ่ายไม่ได้": "option4_node",
    "greeting": "greeting_node",
    "unknown": "unknown_node"
})


builder.add_edge("option1_node", END)
builder.add_edge("option2_node", END)
builder.add_edge("option3_node", END)
builder.add_edge("option4_node", END)
builder.add_edge("unknown_node", END)
builder.add_edge("greeting_node", END)


# Export for FastAPI
# graph = builder.compile()