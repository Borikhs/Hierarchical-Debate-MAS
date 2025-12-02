"""
GroupTeam: A team of 5 agents working together.
"""
from pathlib import Path
from typing import Optional, Annotated

from autogen.coding import LocalCommandLineCodeExecutor, CodeBlock
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat
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

        # Create RoundRobinGroupChat for fixed turn order
        self.team = RoundRobinGroupChat(
            participants=[
                self.researcher,
                self.code_writer,
                self.code_executor, 
                self.analyst,
                self.critic,
                self.leader
            ],
            termination_condition=(
                TextMentionTermination(REPORT_READY_KEYWORD) |
                MaxMessageTermination(MAX_GROUP_MESSAGES)
            )
        )

    def _create_agents(self):

        # 1. Leader: Coordinates the team
        self.leader = AssistantAgent(
            name=f"{self.group_name}Leader",
            description=f"Leader of {self.group_name} who coordinates the team and decides when to continue or stop.",
            model_client=self.model_client,
            system_message=f"""
You are the Leader of {self.group_name}.

Your job is to oversee the entire workflow, integrate the outputs of all agents, 
and decide whether the team should stop or continue to another round.

========================
Responsibilities
========================
1. Supervise the overall reasoning flow and maintain direction.
2. Review and integrate all agent outputs:
   - Researcher's retrieved information
   - CodeWriter's generated code
   - Analyst's interpretation
   - Critic's evaluation and concerns
3. Decide whether the current evidence and reasoning are sufficient.

If the current results ARE sufficient:
- Provide a clear final summary that represents the team's unified conclusion.
- Output the keyword '{REPORT_READY_KEYWORD}' to signal finalization and stop the discussion.

If the results are NOT sufficient:
- Identify missing points or unresolved issues using the Critic's analysis.
- Instruct each agent on what to refine or improve in the next round.
- Produce an improved plan and continue to another round.

========================
Guidelines
- Be concise, decisive, and focused on the task.
- Allow continuation only if it will meaningfully improve the final answer.
- End the discussion once further iterations are unlikely to add new value.
"""
        )

        # 4. Medical Researcher: Searches for medical information using MedRAG
        self.researcher = AssistantAgent(
            name=f"{self.group_name}Researcher",
            description="Searches for medical information using MedRAG and web tools",
            model_client=self.model_client,
            tools=[self.medrag_search_tool],
            system_message="""You are a medical research specialist with access to a medical literature retrieval tool (MedRAG).

Your role:
1. Search for relevant medical information using MedRAG (medrag_search_tool)
2. Retrieve facts from textbooks, medical literature, and clinical knowledge sources
3. Provide medically accurate summaries and evidence-based explanations
4. Cite source information (textbook name, document ID) when possible
5. Return only information that directly helps solve the task

Research Strategy:
- ALWAYS use medrag_search_tool for medical or clinical questions.
- If the tool returns limited results, summarize whatever information is available.
- Do NOT perform web search or use non-medical external information.

Output Guidelines:
- Provide concise, clinically relevant summaries
- Highlight key facts and definitions
- Cite sources clearly when possible (e.g., "Source: Harrison, DocID 1234")
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


        # 2. Code Writer: LLM-based agent that writes code
        self.code_writer = AssistantAgent(
            name=f"{self.group_name}CodeWriter",
            description="Writes executable Python code for emergency room patient data analysis",
            model_client=self.model_client,
            system_message="""
You are an expert Python programmer specializing in medical data analysis.
You must output ONLY Python code.
No explanations, no reasoning, no text

NOTE: The file 'patient_data.csv' already exists in the working directory

# DATASET SCHEMA: patient_data.csv (17,201 rows × 51 columns)

## Key Column
patient_id: Patient unique ID

## Demographics (3)
gender: 0=Female, 1=Male
age: Age in years (0-102)
er_year: ER visit year (2018-2020)

## ER Information (4)
er_stay_hours: ER length of stay (hours)
entry: Entry route (0/1)
ems: EMS use (0=No, 1=Yes)
disposition_type: Discharge type (0=Normal, 1=Transfer, 2=AMA)

## Triage (2)
triage_level: KTAS (1=Resuscitation, 2=Emergent, 3=Urgent, 4=Less urgent, 5=Non-urgent)
initial_avpu: Consciousness (1=Alert, 2=Voice, 3=Pain, 4=Unresponsive)

## Initial Vitals (6)
initial_sbp, initial_dbp: BP (mmHg)
initial_hr: Heart rate (bpm)
initial_rr: Respiratory rate (/min)
initial_bt: Temperature (°C)
initial_spo2: O2 saturation (%) - 39% missing

## Diagnosis (5)
primary_dx_code: ICD-10 code
primary_dx_name: Diagnosis name
injury: 0=Non-trauma, 1=Trauma
num_secondary_dx, total_diagnoses: Diagnosis counts

## Interventions (7) - Binary 0/1
stroke_cp, stemi_cp, cag, transfusion, intubation, ventilator, vasopressor

## Treatment (4)
num_medications, num_lab_tests, num_imaging_tests, num_consultations

## Vital Statistics (15)
sbp_mean/max/min, dbp_mean/max/min, hr_mean/max/min, bt_mean/max/min, spo2_mean/max/min

## Records (4)
num_vital_records, num_medical_records, num_initial_nursing, num_discharge_nursing

---

# CODING GUIDELINES
You write Python code only for **simple descriptive statistics, aggregation, and data exploration.

1. **Data Loading**
   ```python
   import pandas as pd
   df = pd.read_csv('patient_data.csv')
   ```

2. **Handle Missing Data**
   - Check for NaN values before analysis
   - Use .dropna() or .fillna() appropriately
   - Be especially careful with initial_spo2 (39% missing)

3. **Medical Context**
   - Respect clinical significance of values
   - Use proper medical terminology in outputs
   - Consider normal ranges for vitals

4. **Code Structure**
   - Write complete, executable code
   - Use ```python markdown blocks
   - Include error handling
   - Add clear comments
   - Print results with context

5. **Analysis Best Practices**
   - Use descriptive variable names
   - Group by relevant categories (triage_level, gender, etc.)
   - Calculate rates/percentages where appropriate
   - Format medical values with proper units

IMPORTANT: You only WRITE code. You do NOT execute it.
The CodeExecutor will run your code and return results.

Example:
```python
import pandas as pd
import numpy as np

# Load patient data
df = pd.read_csv('patient_data.csv')

# Analyze ER stay by triage level
stay_by_triage = df.groupby('triage_level')['er_stay_hours'].agg(['mean', 'median', 'std'])
print("ER Stay Hours by Triage Level:")
print(stay_by_triage)

# Intervention rates by gender
interventions = ['intubation', 'ventilator', 'vasopressor']
gender_map = {0: 'Female', 1: 'Male'}

print("\nIntervention Rates:")
for intervention in interventions:
    rates = df.groupby('gender')[intervention].mean() * 100
    print(f"\n{intervention.capitalize()}:")
    for g, rate in rates.items():
        print(f"  {gender_map[g]}: {rate:.2f}%")
```
"""
        )


        # Code Executor agent with tool
        self.code_executor = AssistantAgent(
            name=f"{self.group_name}CodeExecutor",
            description="Executes Python code for medical data analysis and returns results",
            model_client=self.model_client,
            tools=[execute_python_code],
            system_message="""You are a code execution specialist.
Your role:
1. When you receive Python code, execute it using the execute_python_code tool
2. Extract code from markdown code blocks if needed
3. Return the execution results clearly
4. Report any errors that occur

NOTE: The file 'patient_data.csv' already exists in the working directory

You DO NOT write code - you only execute code provided by CodeWriter.

When you see code like:
```python
print("hello")
```

Extract the code and call: execute_python_code(code='print("hello")')
Then report the results."""
        )


        # 5. Analyst: Interprets results and validates solutions
        self.analyst = AssistantAgent(
            name=f"{self.group_name}Analyst",
            description="Synthesizes research findings, code results, and user data to produce medical insights.",
            model_client=self.model_client,
            system_message="""You are an expert analyst responsible for synthesizing the given information and generating medical insights relevant to the task.

Your responsibilities:
1. Interpret and integrate the information provided by the Researcher, the results from the CodeExecutor, and the user's input data.
2. Combine these sources to produce new, clinically meaningful analysis directly related to the task.
3. Clearly explain the reasoning and evidence behind your conclusions.
4. Identify whether additional information or analysis would improve the solution.

Guidelines:
- Do NOT evaluate or critique code; only interpret execution results in a clinical context.
- Provide original, synthesized insights rather than repeating others' content.
- Ensure your reasoning is logical, clinically sound, and relevant.
- Keep your analysis concise and clear.

"""
        )

        # 6. Critic: Evaluates weaknesses, errors, and logical flaws
        self.critic = AssistantAgent(
            name=f"{self.group_name}Critic",
            description="Critically evaluates arguments, finds weaknesses, errors, and logical gaps.",
            model_client=self.model_client,
            system_message="""You are a critical evaluator whose purpose is to challenge, test, and stress-test the reasoning provided.

Your responsibilities:
1. Identify logical flaws, unsupported assumptions, or weak reasoning.
2. Point out inconsistencies, over-generalizations, or missing evidence.
3. Challenge conclusions that do not follow strictly from the data.
4. Evaluate whether the Analyst overlooked alternative interpretations.
5. Highlight potential biases or reasoning shortcuts.
6. Suggest corrections or alternative explanations.
7. Ensure that the final conclusion is robust, evidence-based, and logically sound.

Guidelines:
- Be critical but objective; do not accept conclusions without verification.
- Look for edge cases and scenarios the Analyst did not consider.
- Do not simply repeat the Analyst's conclusions—challenge them.
- Provide specific, actionable critiques rather than vague comments.
- Your role is essential to improving the overall quality of the final answer.
"""
)

    async def run(self, task: str):
        result = await self.team.run(task=task)
        return result

    async def run_stream(self, task: str):
        async for message in self.team.run_stream(task=task):
            yield message

