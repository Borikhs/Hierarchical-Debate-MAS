"""
GroupTeam: A team of 5 agents working together.
"""
from pathlib import Path
from typing import Optional, Annotated

from autogen.coding import LocalCommandLineCodeExecutor, CodeBlock
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
import re

from tools import web_search_tool, create_medrag_search_tool, RetrievalSystem
from config import (
    REPORT_READY_KEYWORD,
    MAX_GROUP_MESSAGES,
    CODE_EXECUTION_TIMEOUT,
    USE_VIRTUAL_ENV
)


class GroupTeam:
    """
    A team of 5 specialized agents:
    - Leader: Coordinates the team
    - CodeWriter: Writes Python code (LLM-based)
    - CodeExecutor: Executes code (Non-LLM)
    - Researcher: Searches for information (LLM-based)
    - Analyst: Analyzes results (LLM-based)
    """

    def __init__(
        self,
        group_name: str,
        model_client: OpenAIChatCompletionClient,
        work_dir: Path,
        retrieval_system: Optional[RetrievalSystem] = None
    ):
        self.group_name = group_name
        self.model_client = model_client
        self.retrieval_system = retrieval_system

        # Create isolated work directory for this group
        self.group_work_dir = work_dir / group_name.lower()
        self.group_work_dir.mkdir(parents=True, exist_ok=True)

        # Create MedRAG search tool with shared retrieval system
        if self.retrieval_system is not None:
            self.medrag_search_tool = create_medrag_search_tool(self.retrieval_system)
        else:
            # If no retrieval system provided, create a dummy tool that returns an error
            def medrag_search_tool_dummy(
                query: Annotated[str, "Medical question or query"],
                k: Annotated[int, "Number of documents"] = 5
            ) -> Annotated[str, "Error message"]:
                return "Error: MedRAG retrieval system not initialized"
            self.medrag_search_tool = medrag_search_tool_dummy

        # Initialize agents
        self._create_agents()

        # Create SelectorGroupChat for dynamic coordination
        self.team = SelectorGroupChat(
            participants=[
                self.leader,
                self.code_writer,
                self.code_executor,
                self.researcher,
                self.analyst
            ],
            model_client=model_client,
            selector_prompt=self._get_selector_prompt(),
            termination_condition=(
                TextMentionTermination(REPORT_READY_KEYWORD) |
                MaxMessageTermination(MAX_GROUP_MESSAGES)
            )
        )

    def _create_agents(self):
        """Create all 5 agents for the group."""

        # 1. Leader: Coordinates the team
        self.leader = AssistantAgent(
            name=f"{self.group_name}Leader",
            description=f"Leader of {self.group_name} who coordinates the team",
            model_client=self.model_client,
            system_message=f"""You are the leader of {self.group_name}.

Your responsibilities:
1. Coordinate team members to solve the given task
2. Delegate coding tasks to CodeWriter
3. Ask CodeExecutor to run code after CodeWriter creates it
4. Request Researcher to find information when needed
5. Ask Analyst to interpret results and validate correctness
6. Generate a comprehensive final report when the task is complete

When you have sufficient information and are confident in the solution:
- Summarize the approach taken
- State the final answer clearly
- Use the keyword '{REPORT_READY_KEYWORD}' to indicate completion

Be strategic and efficient in coordinating your team."""
        )

        # 2. Code Writer: LLM-based agent that writes code
        self.code_writer = AssistantAgent(
            name=f"{self.group_name}CodeWriter",
            description="Writes executable Python code to solve problems",
            model_client=self.model_client,
            system_message="""You are an expert Python programmer.

When given a coding task:
1. Write complete, executable Python code
2. Use markdown code blocks with ```python
3. Include proper error handling
4. Add clear comments explaining the logic
5. Make code readable and efficient
6. Print results clearly

IMPORTANT: You only WRITE code. You do NOT execute it.
The CodeExecutor will run your code and return results.

Example format:
```python
# Your code here
def solution():
    # implementation
    pass

result = solution()
print(f"Result: {result}")
```
"""
        )

        # 3. Code Executor: Executes code using a tool
        # Create the executor instance
        self.executor_instance = LocalCommandLineCodeExecutor(
            work_dir=self.group_work_dir,
            timeout=CODE_EXECUTION_TIMEOUT
        )

        # Create a tool function that wraps the executor
        def execute_python_code(
            code: Annotated[str, "Python code to execute"]
        ) -> Annotated[str, "Execution result including output and exit code"]:
            """
            Execute Python code and return the result.

            Args:
                code: Python code to execute

            Returns:
                Execution result with exit code and output
            """
            try:
                result = self.executor_instance.execute_code_blocks(
                    code_blocks=[CodeBlock(language="python", code=code)]
                )
                output = f"Exit code: {result.exit_code}\n"
                output += f"Output:\n{result.output}\n"
                if result.code_file:
                    output += f"Code saved to: {result.code_file}"
                return output
            except Exception as e:
                return f"Error executing code: {str(e)}"

        # Code Executor agent with tool
        self.code_executor = AssistantAgent(
            name=f"{self.group_name}CodeExecutor",
            description="Executes Python code and returns results",
            model_client=self.model_client,
            tools=[execute_python_code],
            system_message="""You are a code execution specialist.

Your role:
1. When you receive Python code, execute it using the execute_python_code tool
2. Extract code from markdown code blocks if needed
3. Return the execution results clearly
4. Report any errors that occur

You DO NOT write code - you only execute code provided by CodeWriter.

When you see code like:
```python
print("hello")
```

Extract the code and call: execute_python_code(code='print("hello")')
Then report the results."""
        )

        # 4. Medical Researcher: Searches for medical information using MedRAG
        self.researcher = AssistantAgent(
            name=f"{self.group_name}Researcher",
            description="Searches for medical information using MedRAG and web tools",
            model_client=self.model_client,
            tools=[self.medrag_search_tool, web_search_tool],
            system_message="""You are a medical research specialist with access to two research tools.

Your role:
1. Search for relevant medical information using MedRAG (medrag_search_tool)
2. Use web search (web_search_tool) for supplementary or non-medical information
3. Gather context and background information from medical literature
4. Find facts, definitions, and explanations from trusted medical sources
5. Summarize findings clearly and cite sources

Research Strategy:
- **ALWAYS use medrag_search_tool FIRST** for medical/clinical questions
  - MedRAG provides access to medical textbooks, clinical guidelines, and literature
  - Best for: disease information, treatments, medical definitions, clinical facts
  - Example: medrag_search_tool(query="What is the pathophysiology of asthma?", k=5)

- Use web_search_tool for:
  - Supplementary information not found in MedRAG
  - Current events or very recent information
  - Non-medical background information
  - Example: web_search_tool(query="latest asthma research 2024")

Output Guidelines:
- Provide concise, relevant summaries
- Highlight key medical information that helps solve the task
- Cite the source (textbook name, document ID) when available
- If MedRAG doesn't have sufficient info, mention this and use web search as backup
"""
        )

        # 5. Analyst: Interprets results and validates solutions
        self.analyst = AssistantAgent(
            name=f"{self.group_name}Analyst",
            description="Analyzes execution results and validates correctness",
            model_client=self.model_client,
            system_message="""You are a data analyst and solution validator.

Your responsibilities:
1. Analyze code execution results
2. Interpret data and outputs
3. Check if results are correct and make sense
4. Identify potential errors or edge cases
5. Suggest improvements if needed
6. Validate solutions against requirements

When analyzing results:
- Be thorough and critical
- Point out any inconsistencies
- Verify calculations and logic
- Consider edge cases
- Provide clear assessments
"""
        )

    def _get_selector_prompt(self) -> str:
        """
        Get the selector prompt for the SelectorGroupChat.
        This prompt guides the selection of the next speaker.
        """
        return f"""Select the next agent to speak based on the current context.

Available agents and their roles:
{{roles}}

Conversation history:
{{history}}

Selection Rules:
1. **Leader** coordinates and decides when to request specific expertise
2. **CodeWriter** creates code (has LLM, writes code only)
3. **CodeExecutor** runs code (no LLM, executes code only)
4. **Workflow**: CodeWriter → CodeExecutor → Analyst is common
5. **Researcher** provides external information when needed
6. **Analyst** interprets execution results and validates correctness
7. After specialists (CodeWriter/CodeExecutor/Researcher/Analyst) speak, often return to **Leader** for coordination

IMPORTANT:
- CodeWriter and CodeExecutor are SEPARATE agents
- CodeWriter writes code, CodeExecutor executes it using tools
- Typical flow: CodeWriter → CodeExecutor → Analyst → Leader

Select the most appropriate agent from: {{participants}}
"""

    async def run(self, task: str):
        """
        Run the team on a given task.

        Args:
            task: The task description

        Returns:
            The result from the team
        """
        result = await self.team.run(task=task)
        return result

    async def run_stream(self, task: str):
        """
        Run the team with streaming output.

        Args:
            task: The task description

        Returns:
            Async stream of results
        """
        async for message in self.team.run_stream(task=task):
            yield message

    def cleanup(self):
        """Clean up resources (e.g., stop code executor)."""
        # Executor cleanup happens automatically, but can be explicit if needed
        pass
