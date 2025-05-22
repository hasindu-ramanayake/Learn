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

def chat_bot(state:State) -> State:
    return { "messages": [llm.invoke(state['messages'])]}

def stream_graph_updates(input_user, graph ):
    for event in graph.stream({"messages":[ {"role":"user", "content":input_user }]}):
        for value in event.values():
            print("Assistant:", value['messages'][0].content)


if __name__ == '__main__':
    graph_builder = StateGraph(State)
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
    llm = init_chat_model("google_genai:gemini-2.0-flash")

    graph_builder.add_node("chat_bot", chat_bot)
    graph_builder.add_edge(START, "chat_bot")

    graph =graph_builder.compile()

    # try:
    #     display(Image(graph.get_graph().draw_mermaid_png()))
    # except Exception:
    #     # This requires some extra dependencies and is optional
    #     pass

    while True:
        try:
            user_input = input("user:" )
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Bye Bye!")
                break
            stream_graph_updates(user_input, graph)
            print()
        except Exception as error:
            print("Didn't work: ", error)


