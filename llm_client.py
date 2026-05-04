import langchain as lc
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
import agents
import prompts



def llm_and_agent(api_key: str):
    if not hasattr(lc, "verbose"):
        lc.verbose = False
    if not hasattr(lc, "debug"):
        lc.debug = False
    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.5
    )

    tools = [agents.wikipedia_tool, agents.youtube_tool, agents.semantic_scholar_tool]
    prompt = prompts.final_prompt
    
    calling_agent = create_tool_calling_agent(llm=llm, tools=tools,prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=calling_agent, tools=tools, verbose=True)

    return agent_executor

