from annotated_types import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv
# debug
from IPython.display import Image, display
from langchain_core.runnables.graph_mermaid import (draw_mermaid_png, MermaidDrawMethod)

load_dotenv()
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

class State(TypedDict):
    messages: Annotated[list[str], add_messages]

class ChatBot:
    def __init__(self, llm):
        self.llm = llm

    def chat_bot(self, state: State):
        print(state['messages'])
        response = self.llm.invoke(state["messages"])
        print(response)
        return {"messages":[response]}

def stream_graph_updates(input_user, graph ):
    for event in graph.stream({"messages":[ {"role":"user", "content":input_user }]}):
        for value in event.values():
            print("Assistant:", value['messages'][0].content)

def route_tools(state: State):
    return "search"
    # return END

if __name__ == '__main__':
    search_duck = DuckDuckGoSearchRun()
    tools = [search_duck]
    # duck_response = search_duck.invoke("First Sri Lankan president")
    # print(duck_response)
    graph_builder = StateGraph(State)
    llm = init_chat_model("google_genai:gemini-2.0-flash", temperature=0)
    llm.bind_tools(tools=tools)
    chat_bot_agent = ChatBot(llm)

    graph_builder.add_edge(START, "chat_bot")
    graph_builder.add_node("chat_bot", chat_bot_agent.chat_bot)
    graph_builder.add_node("search_node", search_duck)
    graph_builder.add_edge("search_node", "chat_bot")
    graph_builder.add_conditional_edges( 
        "chat_bot", 
        route_tools,
        {
            "search":"search_node",
            END:END
        }
    )
    graph = graph_builder.compile()
    
    # debug
    # try:
    #     with open("img.png", "wb") as png:
    #         png.write(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER))
    # except Exception as error:
    #     print(error)

    try:
        user_input = "What do you know about LangGraph?"
        # if user_input.lower() in ["quit", "exit", "q"]:
            # print("Bye Bye!")
            # break
        stream_graph_updates(user_input, graph)
    except Exception as error:
        print("Search didn't work: ", error)
