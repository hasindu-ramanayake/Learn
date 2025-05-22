from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from typing import Union

import os
from dotenv import load_dotenv

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

if __name__ == '__main__':
    llm = init_chat_model("google_genai:gemini-2.0-flash", temperature=0)
    tools = [subtract_tool]
    checkpointer = InMemorySaver()
    agent  = create_react_agent( 
        model=llm.bind_tools(tools),
        tools=tools,
        checkpointer=checkpointer,
        prompt="You are a subtracting tool.")
        
    try:
        config = {"configurable": {"thread_id": "1"}}
        output_agent = agent.invoke({"messages": [{"role":"user", "content":"What is 777-323?"}]}, config=config)
        print(output_agent["messages"][-1])
    except Exception as error:
        print("Didn't work: ", error)