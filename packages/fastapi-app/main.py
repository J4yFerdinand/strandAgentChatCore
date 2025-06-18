import os
import json

from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from strands import Agent
from strands_tools import calculator
from strands.models import BedrockModel
from tools.manage_user_requests import create_user, get_user, update_user, delete_user, list_all_users
from mangum import Mangum


app = FastAPI()

# Create a Bedrock model instance
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0.0,
    top_p=0.1,
    top_k=0.1,
    streaming=False,
)

# Save agent state
def save_agent_state(agent, session_id):
    os.makedirs("sessions", exist_ok=True)

    state = {
        "messages": agent.messages,
        "system_prompt": agent.system_prompt
    }
    # Store state (e.g., database, file system, cache)
    with open(f"sessions/{session_id}.json", "w") as f:
        json.dump(state, f)

# Restore agent state
def restore_agent_state(session_id):
    try:
        # Retrieve state
        with open(f"sessions/{session_id}.json", "r") as f:
            state = json.load(f)

        # Create agent with restored state
        return Agent(
            model=bedrock_model,
            messages=state["messages"],
            system_prompt=state["system_prompt"],
            tools=[calculator, create_user, get_user, update_user, delete_user, list_all_users],
        )
    except FileNotFoundError:
        # Create agent with default values if session doesn't exist
        return Agent(
            model=bedrock_model,
            system_prompt=(
                "Eres un agente capaz de gestionar información de usuarios. Puedes crear, leer y actualizar información de usuarios."
                "Tu objetivo es que funciones como un agente de ventas, el cual deberá responder preguntas relacionadas a la empresa ProIntel, la cual ofrece servicios de Pensión para Colombianos en el Exterior."
                "Deberás hacerle todas las preguntas necesarias al usuario para poder crear o actualizar su información."
                "Puedes ir preguntandolo poco a poco e ir guardando la información que te proporcione."
                "Si el usuario no tiene una cuenta, debes crearla. Si ya tiene una cuenta, debes actualizar su información."
                "Siempre que el usuario te termine de proporcionar información, debes pasar el usuario a revisión manual por un humano."
                "Si un usuario te proporciona un número de documento que ya existe, debes verificar que este usuario NO tenga revisión manual requerida, ya que a los usuarios con revisión manual requerida no se les debe atender mas por medio de este Chat con asistente AI si no un humano, entonces debes reusarte a responder mas o a entablar mas conversación, siempre deberás decir que esta en revisión manual y que debe esperar a que un humano se contacte con usted."
                "Cuando se empieza a pedir información de un usuario, la revisión manual NO es requerida, ya que aun puede que NO tenga toda la información necesaria."
            ),
            tools=[calculator, create_user, get_user, update_user, delete_user, list_all_users],
        )

class Message(BaseModel):
    message: str

class Messages(BaseModel):
    messages: list[Message]

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/chat/{session_id}")
def chat_history(session_id: str):
    try:
        agent = restore_agent_state(session_id)
        return {"messages": agent.messages}
    except FileNotFoundError:
        return {"error": "Session not found"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat/{session_id}")
def chat(session_id: str, message: Message):
    agent = restore_agent_state(session_id)

    # Process the incoming message
    result = agent(message.message)

    # print(f"Received message: {result.message}")
    # print(f"Metrics message: {result.metrics}")
    # print(f"State used: {result.state}")
    # print(f"Stop Reason used: {result.stop_reason}")

    # Save the updated state
    save_agent_state(agent, session_id)

    return {
        "response": result.message.get("content", "")[0].get("text", ""),
    }
    # return {"messages": agent.messages, "result": result.message, "metrics": result.metrics, "state": result.state, "stop_reason": result.stop_reason}

handler = Mangum(app)