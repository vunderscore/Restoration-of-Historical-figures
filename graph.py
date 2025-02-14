import os
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict
import operator
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from pydantic import BaseModel
from tavily import TavilyClient
from dotenv import load_dotenv
from prompts import ID_PROMPT, RESEARCH_PLAN_PROMPT, ANSWER_PROMPT, REFLECT_PROMPT, CRITIQUE_PROMPT, RESEARCH_CRITIQUE_PROMPT

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-001',google_api_key=os.environ["GOOGLE_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

#agent state:- dpecits the structure of the agent's state
class AgentState(TypedDict):
    image_string: str
    figure: str
    query: str
    critique: str
    content: List[str]
    answer: str
    confirm: str
    revision_number: int
    max_revisions: int
    memory: Dict

#Queries defn
class Queries(BaseModel):
    queries: List[str]


#nodes        
def id_node(state: AgentState):
    string = state['image_string']
    usermsg = HumanMessage(
        content=[
        {"type": "text", "text": "who is in this image"},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpg;base64,{string}"},
        },
    ],
    )
    messages = [SystemMessage(content=ID_PROMPT),usermsg]
    response = model.invoke(messages)
    
    #storing identification in memory
    current_memory = state.get('memory',{})
    current_memory['identified_figure'] = response.content
    current_memory['messages'] = current_memory.get('messages',[])
    current_memory['messages'].append({'role':"system",'content':f"identified_figure: {response.content}"})
    return {"figure":response.content,"memory":current_memory}
    
def research_plan_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=[state['figure'],state['query']])
    ])
    
    content = state.get('content',[])
    
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

def answer_node(state: AgentState):
    content = "\n\n".join(state['content'] or [])
    current_memory = state.get('memory',{})
    
    history = current_memory.get('messages', [])
    history_str = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in history
        if msg['role'] != 'system'
    ])
    messages = [SystemMessage(content=ANSWER_PROMPT.format(figure=state['figure'],
                                                           content=content,
                                                           history=history_str)),
               HumanMessage(f"\n\n The question is: {state['query']}")]
    response = model.invoke(messages)
    
    #update memory
    current_memory['messages'].append({'role':'user','content':state['query']})
    current_memory['messages'].append({'role':'assistant','content':response.content})
    return {"answer":response.content,"memory":current_memory}

def reflect_node(state: AgentState):
    messages = [SystemMessage(content=REFLECT_PROMPT.format(figure=state['figure'])),
               HumanMessage(content=state['answer'])]
    response = model.invoke(messages)
    return {"confirm":response.content, "revision_number":state.get("revision_number",1)+1, "memory": state['memory']}

def critique_node(state: AgentState):
    messages = [SystemMessage(content=CRITIQUE_PROMPT.format(figure=state['figure'])),HumanMessage(content=state['answer'])]
    response = model.invoke(messages)
    return {"critique":response.content}

def research_critique_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=state['critique'])
    ])
    content = state.get('content',[])
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

#conditional edge function
def should_continue(state):
    if(state['confirm'].lower() == 'yes' or state['revision_number']>state['max_revisions']):
        return END
    return "c"

# Create workflow
def create_conversation_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("id", id_node)
    workflow.add_node("research_plan", research_plan_node)
    workflow.add_node("answer_node", answer_node)
    workflow.add_node("reflect", reflect_node)
    workflow.add_node("critique_node", critique_node)
    workflow.add_node("critique_plan", research_critique_node)
    
    # Add edges
    workflow.add_edge("id", "research_plan")
    workflow.add_edge("research_plan", "answer_node")
    workflow.add_edge("answer_node", "reflect")
    
    workflow.add_edge("critique_node", "critique_plan")
    workflow.add_edge("critique_plan", "answer_node")
    
    
    # Set conditional edges
    workflow.add_conditional_edges(
        "reflect",
        should_continue,
        {
            "c": "critique_node",
            END: END
        }
    )
    
    #entrypoint
    workflow.set_entry_point("id")
    
    return workflow.compile()