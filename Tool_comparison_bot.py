# %%
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages.ai import AIMessage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

# %%
with open('OpenAIKey.txt', 'r') as f:
    os.environ['OPENAI_API_KEY'] = f.readline()

# %%
chat = ChatOpenAI()

# %%
class Compare(BaseModel):
    objs: list = Field(description="Python list of objects to be compared")
    params: list = Field(description="Python list of comparison parameters")

parser = PydanticOutputParser(pydantic_object=Compare)

# %%
system_prompt = SystemMessagePromptTemplate.from_template('''
Given a task in {framework}, provide a list of relevant objects/tools and comparison parameters. 
If a list of objects/tools and parameters is provided, append additional relevant ones to ensure there are at least five objects and parameters each.
\n{format_instructions}
''')
user_prompt = HumanMessagePromptTemplate.from_template('Task: {task}\nObjects: {objs}\nComparison Parameters: {params}')

prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

# %%
task = 'Web Scraping'
framework = 'Python'
objs = ', '.join(['Scrapy', 'Beautiful Soup'])
params = ', '.join(['Speed'])

res = chat(prompt.format_prompt(task=task, 
                                framework=framework, 
                                objs=objs, params=params, 
                                format_instructions=parser.get_format_instructions()).to_messages())

# %%
print(res.content)

# %%
c = parser.parse(res.content)
objs = c.objs
params = c.params
objs, params

# %%
system_prompt = SystemMessagePromptTemplate.from_template('''
For a task in {framework}, using the list of objects and comparison parameters provided, compare these objects based on qualitative and quantitative data. 
Use the web search tool to gather accurate data for quantitative comparisons.
Give output in JSON format.
''')
user_prompt = HumanMessagePromptTemplate.from_template('Objects: {objs}\nComparison Parameters: {params}')
scratchpad = MessagesPlaceholder("agent_scratchpad")

prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt, scratchpad])

# %%
@tool
def web_scrape(url: str) -> str:
    """
    Scrapes the main heading and paragraphs of a given URL
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        heading = soup.find('h1').get_text() if soup.find('h1') else "No heading found"
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        paragraphs_text = "\n".join(paragraphs) if paragraphs else "No paragraphs found"
        
        return f"Heading: {heading}\n\nParagraphs:\n{paragraphs_text}"

    except requests.RequestException as e:
        return f"Failed to fetch the URL: {e}"

# %%
tools = [web_scrape]
agent = create_openai_tools_agent(chat, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# %%
res2 = agent_executor.invoke({
                       'objs': objs,
                       'params': params,
                       'framework': framework
})

# %%
print(res2['output'])

# %%



