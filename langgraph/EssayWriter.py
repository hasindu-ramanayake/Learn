#this is a original langgraph agent dev flow, used in Deeplearning.ai
from langgraph.graph import StateGraph, END, add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated, Union, List
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
import time

from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv

DEBUG = False

# debug
from IPython.display import Image, display
from langchain_core.runnables.graph_mermaid import (draw_mermaid_png, MermaidDrawMethod)

load_dotenv()
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

class ResearchPlaningOutput(BaseModel):
    queries: List[str]

class AgentState(TypedDict):
    task: str
    plan: str
    content: Annotated[List[str], operator.eq]
    draft: str
    critique: str
    revision_number: int
    max_revisions:int

class Agent:
    def __init__(self, model, tools, system_planner, system_researcher, system_generate, system_crit):
        self.system_message_planner = system_planner
        self.system_message_research = system_researcher
        self.system_message_generate = system_generate
        # self.system_message_reflect = system_reflect
        self.system_message_crit = system_crit
        self.tools = { tool.name: tool for tool in tools}
        self.model = model.bind_tools(tools)
        self.graph = self.generate_tree()
        if DEBUG:
            print(self.tools)

    def generate_tree(self):
        graph_builder = StateGraph(AgentState)
        
        graph_builder.add_node("planner", self.planner_call)
        graph_builder.set_entry_point("planner")
        graph_builder.add_edge("planner", "reasearch_plan")        
        graph_builder.add_node("reasearch_plan", self.research_planner)
        graph_builder.add_edge("reasearch_plan", "generator")
        graph_builder.add_node("generator", self.generate_content)
        graph_builder.set_finish_point("generator")
        graph = graph_builder.compile()
        if DEBUG:
            try:
                with open("img.png", "wb") as png:
                    png.write(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER))
            except Exception as error:
                print(error)
        return graph
    
    def planner_call(self, state:AgentState):
        task = state['task']
        if self.system_message_planner:
            task = [SystemMessage(content=self.system_message_planner)] + task
        output = self.model.invoke(task)
        return {"plan":output.content}

    def research_planner(self, state:AgentState):
        queries = self.model.with_structured_output(ResearchPlaningOutput).invoke([
            SystemMessage(content=self.system_message_research), HumanMessage(content=state["plan"])
        ])

        content = state['content'] or []
        for q in queries.queries:
            time.sleep(5) # to remove the limiter
            response = self.tools['duckduckgo_search'].invoke(q)
            content.append(response)

        return {"content":content}

    def generate_content(self, state:AgentState):
        # print(state['content'])
        data = "\n\n".join(state['content'] or [])
        user_message = HumanMessage(content=f"{data}\n\nHere is my plan{state['plan']}")
        if self.system_message_generate:
            message = [SystemMessage(content=system_prompt_generate), user_message]
        result = self.model.invoke(message)
        return { "draft":result.content, "revision_number":state.get("revision_number",1)+1 }

if __name__ == "__main__":
    
    memory = SqliteSaver.from_conn_string(":memory")
    llm = init_chat_model(model="google_genai:gemini-2.0-flash",checkpoint=memory)
    system_prompt_planner = f""" You are an expert essay writer. You need to breakdown the essay topic to do a research.
    You mush follow the below steps.
    # steps
     - Your goal is to write a five paragraph essay.
     - Identify key areas that need to write.
    """
    system_prompt_research = f""" You are a researcher charged with providing information that can \
    be used when writing the following essay. Generate a list of search queries that will gather \
    any relevant information. Only generate 1 queries max.
    """

    system_prompt_generate = f"""You are an essay assistant tasked with writing excellent 5-paragraph essays.\
    Generate the best essay possible for the user's request and the initial outline. \
    If the user provides critique, respond with a revised version of your previous attempts. \
    Utilize all the information below as needed: 
    ------
    """

    system_prompt_crit = f""" You are a researcher charged with providing information that can \
    be used when making any requested revisions (as outlined below). \
    Generate a list of search queries that will gather any relevant information. Only generate 3 queries max.
    """
    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    
    agent = Agent( 
        model=llm, 
        tools=tools, 
        system_crit=system_prompt_crit,
        system_generate=system_prompt_generate, 
        system_planner=system_prompt_planner, 
        system_researcher= system_prompt_research
        )
    task = [HumanMessage(content="Write and essay about Sri Lanka weather")]
    results = agent.graph.invoke({"task":task})
    print(results["draft"])