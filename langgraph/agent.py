#this is a original langgraph agent dev flow, used in Deeplearning.ai
from langgraph.graph import StateGraph, END, add_messages
from typing import TypedDict, Annotated, Union
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
import time

from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv

# debug
from IPython.display import Image, display
from langchain_core.runnables.graph_mermaid import (draw_mermaid_png, MermaidDrawMethod)

load_dotenv()
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

class SubtractInputSchema(BaseModel):
    """ Subtract two numbers """
    a: Union[int, float] = Field(description="First number")
    b: Union[int, float] = Field(description="Second number")

@tool("subtract_tool", args_schema=SubtractInputSchema )
def subtract_tool(a:[int, float], b:[int, float]) -> [int, float]:
    print(f"Tool 'subtract_tool' called with a={a}, b={b}")
    return a - b

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Agent:
    def __init__(self, model, tools, system="" ):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.create_llm)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm", self.exists_actions,
            {True:"action", False:END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {tool.name: tool for tool in tools}
        self.model = model.bind_tools(tools)

    def exists_actions(self, state:AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0
    
    def create_llm(self, state:AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        messages = self.model.invoke(messages)
        return {"messages": [messages]}

    def take_action(self, state:AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print("calling tool", t)
            if not t['name'] in self.tools:
                print("Bad tool: ", t['name'])
                result = "bad tool name, retry"
            else:
                time.sleep(3)
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(content=str(result), tool_call_id=t['id'], name=t['name']))
        print("back to model")
        return {"messages":results}



if __name__ == '__main__':

    prompt = """You are a smart research assistant. Use the search engine to look up information. \
    You are allowed to make multiple calls (either together or in sequence). \
    Only look up information when you are sure of what you want. \
    If you need to look up some information before asking a follow up question, you are allowed to do that!
    """
    search_duck = DuckDuckGoSearchRun()
    tools = [search_duck, subtract_tool]
    llm = init_chat_model("google_genai:gemini-2.0-flash", temperature=0)
    agent = Agent(model=llm, tools=tools, system=prompt)

    # debug
    try:
        with open("img.png", "wb") as png:
            png.write(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER))
    except Exception as error:
        print(error)

    messages = [HumanMessage(content="What is the weather in Kandy? and answer for 400-100?")]
    result = agent.graph.invoke({"messages": messages})
    # print(result['messages'])

    # query = "Who won the super bowl in 2024? In what state is the winning team headquarters located? \
    # What is the GDP of that state? Answer each question." 
    # messages = [HumanMessage(content=query)]

    # result = agent.graph.invoke({"messages": messages})
    print(result['messages'][-1].content)