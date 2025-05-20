from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from IPython.display import Image, display

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

llm = init_chat_model("google_genai:gemini-2.0-flash")

def chat_bot(state:State) -> State:
    return { "messages": [llm.invoke(state['messages'])]}


graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_edge(START, "chat_bot")

graph =graph_builder.compile()

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass