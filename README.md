# Tool Comparison Bot

This project uses LangChain to compare various tools based on a given framework or programming language. Users can provide their own tools and comparison parameters, and the project will generate a detailed comparison using web scraping for qualitative and quantitative data.

## Features

- **Automatic Tool Suggestion**: Given a task and a framework, the project suggests relevant tools.
- **Customizable Parameters**: Users can provide their own comparison parameters.
- **Web Scraping**: Utilizes web scraping to gather data for comparisons.
- **JSON Output**: Provides comparison results in JSON format.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pran-ayyy/tool-comparison-bot.git
   cd langchain-tool-comparison
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use \`venv\\Scripts\\activate\`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your OpenAI API key:
   - Create a file named `OpenAIKey.txt` in the root directory.
   - Add your OpenAI API key in this file.

## Usage

1. Import necessary modules and initialize the chat model:
   ```python
   from langchain.prompts import (
       ChatPromptTemplate,
       HumanMessagePromptTemplate,
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

   # Load OpenAI API key
   with open('OpenAIKey.txt', 'r') as f:
       os.environ['OPENAI_API_KEY'] = f.readline()

   chat = ChatOpenAI()
   ```

2. Define the `Compare` model and the system/user prompts: (Optional)
   ```python
   class Compare(BaseModel):
       objs: list = Field(description="Python list of objects to be compared")
       params: list = Field(description="Python list of comparison parameters")

   parser = PydanticOutputParser(pydantic_object=Compare)

   system_prompt = SystemMessagePromptTemplate.from_template('''
   Given a task in {framework}, provide a list of relevant objects/tools and comparison parameters. 
   If a list of objects/tools and parameters is provided, append additional relevant ones to ensure there are at least five objects and parameters each.
   \n{format_instructions}
   ''')
   user_prompt = HumanMessagePromptTemplate.from_template('Task: {task}\nObjects: {objs}\nComparison Parameters: {params}')

   prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])
   ```

3. Example of generating a list of tools and comparison parameters:
   ```python
   task = 'Web Scraping'
   framework = 'Python'
   objs = ', '.join(['Scrapy', 'Beautiful Soup'])
   params = ', '.join(['Speed'])

   res = chat(prompt.format_prompt(task=task, 
                                   framework=framework, 
                                   objs=objs, params=params, 
                                   format_instructions=parser.get_format_instructions()).to_messages())

   c = parser.parse(res.content)
   objs = c.objs
   params = c.params
   ```

4. Define a web scraping tool and create the agent:
   ```python
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
           paragraphs_text = "\\n".join(paragraphs) if paragraphs else "No paragraphs found"

           return f"Heading: {heading}\\n\\nParagraphs:\\n{paragraphs_text}"

       except requests.RequestException as e:
           return f"Failed to fetch the URL: {e}"

   tools = [web_scrape]
   agent = create_openai_tools_agent(chat, tools, prompt)
   agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
   ```

5. Generate the comparison:
   ```python
   res2 = agent_executor.invoke({
                          'objs': objs,
                          'params': params,
                          'framework': framework
   })

   print(res2['output'])
   ```

## Example

The following example demonstrates how to compare web scraping tools in Python:

```python
task = 'Web Scraping'
framework = 'Python'
objs = ', '.join(['Scrapy', 'Beautiful Soup'])
params = ', '.join(['Speed'])

res = chat(prompt.format_prompt(task=task, 
                                framework=framework, 
                                objs=objs, params=params, 
                                format_instructions=parser.get_format_instructions()).to_messages())

c = parser.parse(res.content)
objs = c.objs
params = c.params

res2 = agent_executor.invoke({
                          'objs': objs,
                          'params': params,
                          'framework': framework
})

print(res2['output'])
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

