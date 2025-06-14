from typing import Annotated, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from IPython.display import Image, display

#pdf to .md file
import pymupdf4llm
import pathlib
import fitz
from langchain_community.document_loaders import PyMuPDFLoader

from IPython.display import Image, display
from langchain_core.runnables.graph_mermaid import (draw_mermaid_png, MermaidDrawMethod)

from output_format import *

load_dotenv()
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
AGENT_DEBUG= True

llm = init_chat_model(model="google_genai:gemini-2.0-flash")

class AgentState(TypedDict):
    file_path: list[str]
    user_cv: str
    cv_breakdown: dict
    job_description: str
    jd_outline: str
    cv_data: Annotated[List[str], add_messages]
    reflect: str
    template: str
    num_revision: int
    max_revision: int

def convert_pdf_to_md_file(state:AgentState):
    file = open("convert.md", "r")
    cv = file.read()
    return { "user_cv": cv }
    ''' original code. do not delete
        docs = []
        for file in state['file_path']:
            loader = PyMuPDFLoader(file_path=file)
            docs_lazy = loader.lazy_load()

            for doc in docs_lazy:
                docs.append(doc)
            # print(docs[0].page_content[:100])
            # print(docs[0].metadata)
            # num_pages = pymupdf4llm.count_pages(state['file_path'])
            # print(fitz.open(state['file_path']).page_count)
            # all_pages = list(range(0, fitz.open(state['file_path']).page_count))
            # md_text = pymupdf4llm.to_markdown(state['file_path'], pages=all_pages )
            # cv = md_text.encode()
        cv = docs
        # pathlib.Path("convert.md").write_bytes(cv[0].page_content)
        file = open("convert.md", "w")
        for page in cv:
            file.write(page.page_content)
            file.write("\n----------------\n")
        file.close()
    '''

def extract_JD(state:AgentState):
    system_prompt = """ You are an expert Job Description Analyst, skilled at extracting key information and generating comprehensive job descriptions from various sources. Your goal is to provide a clear and detailed understanding of the responsibilities, requirements, and expectations of a given job, tailored for use in crafting effective CVs (resumes).
        **Your Task:**
        Given a job advertisement, job title, a brief description of the role, or any combination thereof, analyze the input and perform the following:

        1.  **Extraction (if possible):**  If a job advertisement or detailed description is provided, meticulously extract the following information:
            *   **Job Title:** (The official name of the position)
            *   **Responsibilities/Duties:** (A bulleted list of specific tasks, activities, and duties the employee will perform)
            *   **Required Skills:** (Technical skills, software proficiency, tools, methodologies, etc.)
            *   **Required Qualifications:** (Education, experience level, certifications, licenses, etc.)
            *   **Preferred Skills/Qualifications:** (Skills and qualifications that are beneficial but not strictly required)
            *   **Keywords:** (Identify relevant keywords related to the job and industry for use in a CV)

        2.  **Generation (if extraction is limited or impossible):** If the provided input is minimal (e.g., just a job title), generate a realistic and comprehensive job description based on your knowledge of typical responsibilities, skills, and qualifications for that role, focusing on information relevant to CV creation.  Use industry standards and best practices to create a well-rounded description.  Make educated assumptions if necessary, but clearly state when you are generating information rather than extracting it.

        3. **Output Format:**

        **Job Description:**
        [A concise paragraph summarizing the overall purpose and scope of the role.  This paragraph should highlight the key responsibilities and contribution to the organization.]
        **Responsibilities/Duties:**
        *   [Extracted/Generated Duty 1]
        *   [Extracted/Generated Duty 2]
        *   [Extracted/Generated Duty 3]
            ...
        **Required Skills:**
        *   [Extracted/Generated Skill 1]
        *   [Extracted/Generated Skill 2]
        *   [Extracted/Generated Skill 3]
            ...
        **Required Qualifications:**
        *   [Extracted/Generated Qualification 1]
        *   [Extracted/Generated Qualification 2]
        *   [Extracted/Generated Qualification 3]
            ...
        **Preferred Skills/Qualifications:**
        *   [Extracted/Generated Preferred Skill 1]
        *   [Extracted/Generated Preferred Skill 2]
            ...
        **Keywords:** [List of relevant keywords for CV optimization, e.g., Project Management, Python, Data Analysis, Customer Service]

        **Important Considerations:**

        *   **Focus on Action Verbs:**  When generating responsibilities, use strong action verbs (e.g., "Developed," "Managed," "Implemented," "Analyzed").
        *   **Quantifiable Results:** Where possible, generate responsibilities that suggest potential for quantifiable results (e.g., "Improved efficiency by 15%").
        *   **Relevance to CV:** Prioritize information that would be most useful for someone writing a CV for this position.
        *   **Clarity and Conciseness:** Ensure the generated descriptions are easy to understand and free of jargon, unless the jargon is standard for the industry.
        *   **Disclaimers:** If generating information, explicitly state: "Generated based on typical responsibilities and requirements for this role."

        **Example Input (Partial):**

        "Job Title: Software Engineer, Junior.  We are looking for a motivated Software Engineer to join our team.  Responsibilities include coding in Java and Python, and working with databases."
        **Example Output (Partial):**
        **Job Description:**
        The Junior Software Engineer is responsible for developing, testing, and maintaining software applications using Java and Python. This role involves working collaboratively with a team to implement new features, debug existing code, and contribute to the overall architecture of the system.
        **Responsibilities/Duties:**
        *   Write clean, efficient, and well-documented code in Java and Python.
        *   Develop and maintain databases.
        *   Participate in code reviews and testing.
            ...
        **Now, analyze the following job information:** """

    jd = [SystemMessage(content=system_prompt), HumanMessage(content=state['job_description'])]
    return {'jd_outline':llm.invoke(jd)}


def extract_user_data(state:AgentState):
    system_prompt = """
        You are an AI assistant which help user to extract below data from the user input
        # EXTRACT INFORMATION #
            - full name
            - LinkedIn profile link
            - GitHub profile  link
            - Email Address
            - Telephone number
        """
    jd = [SystemMessage(content=system_prompt), HumanMessage(content=state['user_cv'])]
    return {'cv_breakdown':{"user_info":llm.with_structured_output(user_info_json).invoke(jd)}}

def extract_professional_work(state:AgentState):
    system_prompt = """
        You are an AI assistant which help user to extract below data from the user input
        # EXTRACT INFORMATION #
            - professional work experience | Company name | date (if data provided)
        """
    jd = [SystemMessage(content=system_prompt), HumanMessage(content=state['user_cv'])]
    return {'cv_breakdown':{"professional":llm.with_structured_output(position_worked).invoke(jd)}}

def extract_non_professional_work(state:AgentState):
    system_prompt = """
        You are an AI assistant which help user to extract below data from the user input
        # EXTRACT INFORMATION # 
            - non-professional positions | date (if data provided)
        """
    jd = [SystemMessage(content=system_prompt), HumanMessage(content=state['user_cv'])]
    return {'cv_breakdown':{"non_professional":llm.with_structured_output(position_worked).invoke(jd)}}

def exctract_working_experience(state:AgentState):
    system_prompt = """
        You are an AI assistant which help user to extract below data from the user input
        # EXTRACT INFORMATION # 
            - Extract project information
                - Contribution
        """
    jd = [SystemMessage(content=system_prompt), HumanMessage(content=state['user_cv'])]
    return {'cv_breakdown':{"projects":llm.invoke(jd)}}

def exctract_skills_experience(state:AgentState):
    system_prompt = """
        You are an AI assistant which help user to extract below data from the user input
        # EXTRACT INFORMATION # 
            - Extract skill information
                - Technical and non-technical skills
        """
    jd = [SystemMessage(content=system_prompt), HumanMessage(content=state['user_cv'])]
    return {'cv_breakdown':{"skills":llm.invoke(jd)}}
    
def generate_cv(state:AgentState):
    system_prompt = """"Analyze the following job description outline {jd_outline} and the following CV {user_cv}.  Identify the qualifications and skills mentioned in the job description that are demonstrably present in the CV. For each match, provide a brief (1-2 sentence) explanation of *how* the CV demonstrates that qualification or skill. Focus on specific examples and quantifiable achievements mentioned in the CV.
        Prioritize qualifications that are explicitly mentioned in the `jd_outline`'s 'Responsibilities' and 'Requirements' sections (if applicable).  If a qualification is only weakly supported or absent from the CV, note this briefly (e.g., "Weakly supported - CV mentions [related skill] but lacks specific examples in [area]."). Only include qualifications for which there is some evidence in the CV, even if weak. Do not make assumptions or fabricate information not present in the CV. Be concise and professional in your explanations.
        **IMPORTANT:** If the `jd_outline` specifies desired years of experience, explicitly mention whether the CV meets or falls short of that requirement for each relevant skill area.
        **Example:**
        Let's say the `jd_outline` includes "5+ years of experience in project management" and the CV shows 7 years leading projects.  The output should include:
        Now, replace `jd_outline` and `user_cv` with the actual text of the job description outline and the user's CV, respectively.
        use the user given template for output:
        {input}
        """
    # print(state["jd_outline"])
    prompt_variables = {
        "jd_outline": state["jd_outline"], 
        "user_cv": state["user_cv"], 
        "input": state["template"]
    }
    jd = SystemMessage(content=system_prompt).content.format(**prompt_variables)
    return { 'cv_data': [llm.invoke(jd)] }



if __name__ == "__main__":
    file_paths = ["./test.pdf", "./Profile.pdf"]
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("PDF_to_MD_converter", convert_pdf_to_md_file)
    graph_builder.add_node("extract_jd", extract_JD)
    graph_builder.add_node("extract_user_data", extract_user_data)
    graph_builder.add_node("extract_experiances", extract_professional_work)
    graph_builder.add_node("extract_non_professional_work", extract_non_professional_work)
    graph_builder.add_node("exctract_working_experience", exctract_working_experience)
    graph_builder.add_node("exctract_skills_experience", exctract_skills_experience)

    
    
    graph_builder.add_edge(START, "PDF_to_MD_converter")
    graph_builder.add_edge("PDF_to_MD_converter","extract_jd")
    graph_builder.add_edge("extract_jd","extract_user_data")
    graph_builder.add_edge("extract_user_data","extract_experiances")
    graph_builder.add_edge("extract_experiances","extract_non_professional_work")
    graph_builder.add_edge("extract_non_professional_work","exctract_working_experience")
    graph_builder.add_edge("exctract_working_experience","exctract_skills_experience")
    graph_builder.add_edge("exctract_skills_experience", END)

    graph = graph_builder.compile()
    # DEBUG image
    try:
        with open("img.png", "wb") as png:
            png.write(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER))
    except Exception as error:
        print(error)
    jd = "I need to create my CV for waiter job."

    template = """# 
        [Your Full Name]
        TP      :[Your Phone Number]
        Email   :[Your Email Address] 
        LinkedIn:[Your LinkedIn Profile URL]
        GitHub  :[Your GitHub account URL]
        ____    
        ## Summary/Objective

        [A brief (2-3 sentence) overview of your skills and career goals. Tailor this to each job you apply for. Focus on what you can offer the employer.]

        ## Skills

        **Technical Skills:** [List technical skills, separated by commas.  Example: Python, Java, SQL, Git, AWS, Docker, Kubernetes]
        **Soft Skills:** [List soft skills, separated by commas. Example: Communication, Leadership, Teamwork, Problem-solving, Time Management]
        
        ## Experience
        ### [Job Title1], [Company Name], [City, State]  | [Start Date] - [End Date]
        ### [Job Title2], [Company Name], [City, State]  | [Start Date] - [End Date]
        ### [Job Title2], [Company Name], [City, State]  | [Start Date] - [End Date]

        ###[Experience 1]:
        * [related Project description or outline]
        * [project responsibilities or contribution]
        * [project rewards/recognitions if any]

        share relavant experience as N time...
        
        ###[Experience N]:
        * [related Project description or outline]
        * [project responsibilities or contribution]
        * [project rewards/recognitions if any]

        ## Education

        ### [Degree Name] 
        # [Major]
        # [University Name]
        # [City, State]
        
        ## Personal Projects and activities  (Optional)
        ### [Personal Projects and activity]
        *   [Brief description of the project.]
        *   [Technologies used.]
        *   [Link to the project (e.g., GitHub repository) if available.]

        ### [Personal Project and activity ]
        *   [Brief description of the project.]
        *   [Technologies used.]
        *   [Link to the project (e.g., GitHub repository) if available.]

        ## Volunteer Experience
        ### [Organization Name], [Role]
        *   [Description of your responsibilities and accomplishments.]

        ## Awards & Recognition (Optional)
        *   [Award Name], [Awarding Organization], [Date]
        *   [Another Award Name], [Awarding Organization], [Date]

        ## Certifications (Optional)
        *   [Certification Name], [Certifying Organization], [Date]
        *   [Another Certification Name], [Certifying Organization], [Date]
        
        """


    result = None
    for result in graph.stream({"file_path":file_paths, "max_revision":2, "num_revision":0, "job_description": jd, "template":template}):
        result = result

    # json_data = ast.literal_eval(json.dumps(result["extract_user_data"]["cv_breakdown"]["user_info"]))
    # json_data = json.loads(json.dumps(result["exctract_working_experience"]["cv_breakdown"]["projects"].content))
    # print(json_data)
    # print(result)
    file = open("temp.md", "w")
    file.write(str(result["exctract_skills_experience"]["cv_breakdown"]["skills"].content))
    file.close()

