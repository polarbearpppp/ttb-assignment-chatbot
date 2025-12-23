from ai_agent import builder 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

memory = MemorySaver()
graph_compiled = builder.compile(checkpointer=memory)

class ChatRequest(BaseModel):
    user_input: str
    thread_id: str

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # 1. Run the Graph
        output = await graph_compiled.ainvoke(
            {"user_input": request.user_input}, 
            config=config
        )
        
        ai_response = output.get("final_output", "")
        # Get the metadata dictionary we captured in the node
        metadata = output.get("raw_metadata", {})
        decision = output.get("decision")

        # 2. SAVE LOG (Fixed the arguments here)
        save_chat_to_audit_log(
            thread_id=request.thread_id,
            user_query=request.user_input,
            bot_response=ai_response,
            raw_metadata=metadata,
            decision=decision
        )
        
        # 3. Return everything to the Frontend
        return {
            "response": ai_response,
            "metadata": metadata, 
            "decision": decision
        }
        
    except Exception as e:
        print(f"Error: {e}") # Print the real error to your terminal
        raise HTTPException(status_code=500, detail="Internal Server Error")

# FIXED: Added 'bot_response' to the parameters
def save_chat_to_audit_log(thread_id, user_query, bot_response, raw_metadata, decision):
    """
    Simulates a banking audit log.
    In production, this would write to a SQL table or a secure CSV.
    """
    log_entry = (
        f"\n{'='*50}\n"
        f"AUDIT LOG - Thread: {thread_id}\n"
        f"Input: {user_query}\n"
        f"Decision: {decision}\n"
        f"Output: {bot_response}\n"
        f"Metadata: {raw_metadata}\n"
        f"{'='*50}\n"
    )
    print(log_entry)
    
    # Optional: Save to a local file for the assignment
    with open("chat_audit_log.txt", "a") as f:
        f.write(log_entry)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)