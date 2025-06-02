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
from langchain_core.rate_limiters import InMemoryRateLimiter
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

class Agent:
    def __init__(self, model, tools, system_planner, system_researcher, system_generate, system_reflect, system_crit, max_revisions, memory):
        self.system_message_planner = system_planner
        self.system_message_research = system_researcher
        self.system_message_generate = system_generate
        self.system_message_reflect = system_reflect
        self.system_message_crit = system_crit
        self.memory = memory
        self.max_revisions = max_revisions
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
        graph_builder.add_conditional_edges(
            "generator",
            self.do_a_rework,
            {
                END:END, 
                "reflect":"reflect"
            }
        )
        graph_builder.add_node("reflect", self.reflect_agent)
        graph_builder.add_edge("reflect", "re_critique")
        graph_builder.add_node("re_critique", self.research_critique)
        graph_builder.add_edge("re_critique", "generator")
        # graph_builder.set_finish_point("re_critique")
        graph = graph_builder.compile(checkpointer=self.memory)
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
            message = [SystemMessage(content=self.system_message_generate), user_message]
        result = self.model.invoke(message)
        return { "draft":result.content, "revision_number":state.get("revision_number",1)+1 }

    def do_a_rework(self, state:AgentState):
        if self.max_revisions >= state['revision_number']:
            return "reflect"
        return END
        
    def reflect_agent(self, state:AgentState):
        message = HumanMessage(content=state['draft'])
        if self.system_message_reflect:
            message = [ SystemMessage(content=self.system_message_reflect), HumanMessage(content=state['draft'])]
        response = self.model.invoke(message)
        return {"critique": response.content}

    def research_critique(self, state:AgentState):
        queries = self.model.with_structured_output(ResearchPlaningOutput).invoke([
            SystemMessage(content=self.system_message_crit), HumanMessage(content=state["critique"])
        ])

        content = state['content'] or []
        for q in queries.queries:
            time.sleep(5) # to remove the limiter
            response = self.tools['duckduckgo_search'].invoke(q)
            content.append(response)
        if DEBUG:
            print("research_critique: ", content)

        return {"content":content}


if __name__ == "__main__":
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.1,  # <-- Super slow! We can only make a request once every 10 seconds!!
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
        max_bucket_size=10,  # Controls the maximum burst size.
    )
    llm = init_chat_model(model="google_genai:gemini-2.0-flash")
    system_prompt_planner = """ You are an expert essay writer. You need to breakdown the essay topic to do a research.
    You mush follow the below steps.
    # steps
     - Your goal is to write a five paragraph essay.
     - Identify key areas that need to write.
    """
    system_prompt_research = """ You are a researcher charged with providing information that can \
    be used when writing the following essay. Generate a list of search queries that will gather \
    any relevant information. Only generate 1 queries max.
    """

    system_prompt_generate = """You are an essay assistant tasked with writing excellent 5-paragraph essays.\
    Generate the best essay possible for the user's request and the initial outline. \
    If the user provides critique, respond with a revised version of your previous attempts. \
    Utilize all the information below as needed: 
    ------
    {content}
    """

    system_prompt_reflect = """You are a teacher grading an essay submission. \
    Generate critique and recommendations for the user's submission. \
    Provide detailed recommendations, including requests for length, depth, style, etc."""
    
    system_prompt_crit = """ You are a researcher charged with providing information that can \
    be used when making any requested revisions (as outlined below). \
    Generate a list of search queries that will gather any relevant information. Only generate 3 queries max.
    """
    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    with SqliteSaver.from_conn_string(":memory:") as checkpointer:
        agent = Agent( 
            model=llm, 
            tools=tools, 
            system_crit=system_prompt_crit,
            system_generate=system_prompt_generate, 
            system_planner=system_prompt_planner, 
            system_reflect=system_prompt_reflect,
            system_researcher= system_prompt_research, 
            max_revisions=2, 
            memory=checkpointer
            )

        task = [HumanMessage(content="Write and essay about Sri Lanka weather")]
        thread = {"configurable": {"thread_id": "1"}}
        result = None
        for result in agent.graph.stream({"task":task, "revision_number":1},thread):
            result = result
        print(result["generator"]["draft"])
    