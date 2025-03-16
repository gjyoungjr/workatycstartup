import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor

# Set your API key
os.environ["GROQ_API_KEY"] = "your-groq-api-key"

# Initialize the Llama 3 model on Groq
model = ChatGroq(
    model="llama3-70b-8192",  # Llama 3 70B model
    temperature=0,  # Set to 0 for more deterministic responses
)

# Define some example tools
@tool
def search(query: str) -> str:
    """Search the web for information about a specific query."""
    # In a real implementation, you'd connect to a search API
    return f"Found results for: {query}"

@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating: {e}"

@tool
def get_current_weather(location: str) -> str:
    """Get the current weather for a location."""
    # In a real implementation, you'd connect to a weather API
    return f"The weather in {location} is sunny and 75°F"

# List of tools available to the agent
tools = [search, calculate, get_current_weather]

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant. You have access to the following tools:
    
{tools}

Use these tools to best assist the user. Always think step-by-step about what the user is asking and which tool would be most appropriate.
When you use a tool, wait for its response before proceeding.
"""),
    ("human", "{input}"),
])

# Create the agent
agent = create_openai_tools_agent(model, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Set to True to see the agent's thought process
)

# Run the agent
def run_agent(user_input):
    response = agent_executor.invoke({"input": user_input})
    return response["output"]
