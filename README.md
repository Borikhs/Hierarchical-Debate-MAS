# Multi-Agent Collaborative Debate System

A sophisticated multi-agent system using AutoGen that implements hierarchical collaborative problem-solving through independent group work and leader debate.

## Architecture

### Two-Phase Approach

**Phase 1: Parallel Group Processing**
- 3 independent groups work simultaneously on the same task
- Each group has 5 specialized agents:
  - **Leader**: Coordinates the team
  - **CodeWriter**: Writes Python code (LLM-based)
  - **CodeExecutor**: Executes code (Non-LLM, uses LocalCommandLineCodeExecutor)
  - **Researcher**: Searches for information
  - **Analyst**: Analyzes results and validates correctness
- Groups do not communicate with each other in Phase 1
- Each group generates an independent solution/report

**Phase 2: Leader Debate & Consensus**
- The 3 group leaders present their findings
- Leaders debate different approaches
- Consensus Manager facilitates discussion
- Final consensus answer is synthesized

## Project Structure

```
Hierarchical-Debate-MAS/
├── agents/              # (Reserved for custom agents)
├── teams/
│   ├── group_team.py   # GroupTeam class (5 agents)
│   └── __init__.py
├── orchestration/
│   ├── phase1_parallel.py   # Phase 1 orchestrator
│   ├── phase2_debate.py     # Phase 2 debate system
│   └── __init__.py
├── tools/
│   ├── web_search.py   # Web search tool
│   └── __init__.py
├── config/
│   ├── settings.py     # Configuration
│   └── __init__.py
├── examples/
│   └── simple_test.py  # Test examples
├── coding/             # Code execution workspace (auto-created)
├── .log/               # Log files (auto-created)
├── .env                # Environment variables (create this)
├── main.py             # Main system
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.10+
- Conda environment (recommended)
- OpenAI API key

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Hierarchical-Debate-MAS.git
cd Hierarchical-Debate-MAS/

# Activate conda environment
conda activate multiagent

# Install dependencies
pip install autogen autogen-agentchat autogen-ext openai python-dotenv

# Create .env file and add your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Usage

### Basic Usage

```python
import asyncio
from main import MultiAgentDebateSystem

async def solve_problem():
    # Create system (logging enabled by default)
    system = MultiAgentDebateSystem()

    # Define task
    task = "Calculate the 15th Fibonacci number using code."

    # Run the system
    result = await system.run(task, verbose=True)

    # Access results
    print("Final Answer:", result['final_answer'])
    print("Logs saved to:", result['log_directory'])

    # Cleanup
    system.cleanup()

# Run
asyncio.run(solve_problem())
```

### Disabling Logging

```python
# Disable transcript logging
system = MultiAgentDebateSystem(enable_logging=False)
```

### Custom Log Directory

```python
from pathlib import Path

# Save logs to custom directory
system = MultiAgentDebateSystem(log_dir=Path("my_logs"))
```

### Running Examples

```bash
# Navigate to Hierarchical-Debate-MAS directory
cd Hierarchical-Debate-MAS

# Run simple test (10th Fibonacci)
conda run -n multiagent python examples/simple_test.py --test simple

# Run complex test (Fibonacci primes)
conda run -n multiagent python examples/simple_test.py --test complex

# Or run main.py directly
conda run -n multiagent python main.py
```

## Configuration

Edit `config/settings.py` to customize:

```python
# Model configuration
MODEL_NAME = "gpt-4o"  # or "gpt-4", "gpt-3.5-turbo", etc.

# Agent configuration
MAX_GROUP_MESSAGES = 25  # Max messages per group in Phase 1
MAX_DEBATE_ROUNDS = 5    # Max debate rounds in Phase 2

# Code execution
CODE_EXECUTION_TIMEOUT = 60  # seconds
USE_VIRTUAL_ENV = False      # Use isolated venv per group
```

## How It Works

### Phase 1: Parallel Execution

1. System creates 3 identical `GroupTeam` instances
2. Each group receives the same task
3. All groups run in parallel using `asyncio.gather()`
4. Within each group:
   - Leader coordinates the team
   - CodeWriter creates solution code
   - CodeExecutor runs the code
   - Analyst validates results
   - Leader generates final report
5. Phase 1 returns 3 independent reports

### Phase 2: Debate

1. System creates leader agents initialized with Phase 1 reports
2. Consensus Manager facilitates the debate
3. Leaders present their approaches
4. Discussion continues until:
   - All agree on an answer
   - ConsensusManager synthesizes final answer
   - Max debate rounds reached
5. Final consensus is returned

### Example Output Flow

```
PHASE 1: PARALLEL GROUP EXECUTION
==================================
Task: Calculate 10th Fibonacci number

Running 3 groups in parallel...

Starting Group1...
  Group1Leader: Let's solve this step by step
  Group1CodeWriter: Here's the code...
  Group1CodeExecutor: [Executes code]
  Group1Analyst: Result is correct: 55
  Group1Leader: REPORT_READY. Answer: 55

Starting Group2...
  [Similar process, might use different approach]

Starting Group3...
  [Similar process, might use different approach]

PHASE 1 COMPLETED
=================

Group1 Report: Answer is 55 using recursive approach
Group2 Report: Answer is 55 using iterative approach
Group3 Report: Answer is 55 using formula approach

PHASE 2: LEADER DEBATE
=======================

Group1Leader: We used recursion and got 55
Group2Leader: We used iteration and got 55
Group3Leader: We used Binet's formula and got 55
ConsensusManager: All three groups agree. The 10th Fibonacci number is 55.
CONSENSUS_REACHED

FINAL CONSENSUS
===============
The 10th Fibonacci number is 55. All three groups independently
arrived at the same answer using different approaches (recursive,
iterative, and mathematical formula), which validates the correctness.
```

## Key Features

### 1. Independent Group Work
- True parallel execution
- No inter-group communication in Phase 1
- Different approaches emerge naturally

### 2. Code Execution Safety
- LocalCommandLineCodeExecutor for safe execution
- Isolated work directories per group
- Timeout protection
- Tool-based execution (compatible with AgentChat API)

### 3. Structured Debate
- SelectorGroupChat for dynamic speaker selection
- Consensus Manager for fair facilitation
- Multiple termination conditions

### 4. Automatic Transcript Logging
- **NEW**: All conversations saved to timestamped directories
- Phase 1: Individual group transcripts (3 files)
- Phase 2: Leader debate transcript (1 file)
- Summary file with overview
- Both human-readable (.txt) and JSON formats

### 5. Flexibility
- Easy to configure (see `config/settings.py`)
- Swappable models (GPT-4, GPT-3.5, etc.)
- Extensible agent roles
- Optional logging (can be disabled)

## Transcript Logging

### Overview

By default, the system automatically saves all conversations to timestamped directories in `tmp/transcripts/`.

### Log Directory Structure

```
tmp/transcripts/
└── 20250110_143022/           # Timestamped session
    ├── session_summary.txt     # Overview of entire session
    ├── phase1_group1.txt       # Group 1 internal discussion
    ├── phase1_group1.json      # Group 1 (JSON format)
    ├── phase1_group2.txt       # Group 2 internal discussion
    ├── phase1_group2.json      # Group 2 (JSON format)
    ├── phase1_group3.txt       # Group 3 internal discussion
    ├── phase1_group3.json      # Group 3 (JSON format)
    ├── phase2_leader_debate.txt  # Leader debate
    └── phase2_leader_debate.json # Leader debate (JSON format)
```

### Accessing Logs

```python
result = await system.run(task)

# Get log directory
log_dir = result['log_directory']
print(f"Logs saved to: {log_dir}")

# Read a specific transcript
with open(log_dir / "phase1_group1.txt", 'r') as f:
    print(f.read())

# Parse JSON format for programmatic access
import json
with open(log_dir / "phase1_group1.json", 'r') as f:
    data = json.load(f)
    for msg in data['messages']:
        print(f"{msg['source']}: {msg['content'][:50]}...")
```

### Configuration

```python
# Enable logging (default)
system = MultiAgentDebateSystem(enable_logging=True)

# Disable logging
system = MultiAgentDebateSystem(enable_logging=False)

# Custom log directory
from pathlib import Path
system = MultiAgentDebateSystem(log_dir=Path("my_custom_logs"))
```

### Use Cases

1. **Debugging**: Review exact agent conversations to debug issues
2. **Analysis**: Analyze how different groups approached the same problem
3. **Research**: Study multi-agent collaboration patterns
4. **Auditing**: Keep records of AI decision-making processes
5. **Improvement**: Identify areas where agents could perform better

## Troubleshooting

### "OpenAI API key not found"
```bash
# Create or edit .env file in Hierarchical-Debate-MAS directory
echo "OPENAI_API_KEY=your-key-here" > .env
```

### "Module not found" errors
```bash
# Make sure you're in the right directory and environment
conda activate multiagent
# Reinstall dependencies if needed
pip install autogen autogen-agentchat autogen-ext openai python-dotenv
```

### Code execution fails
- Check that the `coding/` directory is writable
- Verify Python is accessible in your environment
- Check CODE_EXECUTION_TIMEOUT in settings

### Groups taking too long
- Reduce MAX_GROUP_MESSAGES in config
- Use a faster model (e.g., gpt-3.5-turbo)
- Simplify the task

## Development

### Adding New Tools

Create a new tool in `tools/`:

```python
# tools/my_tool.py
def my_tool(param: str) -> str:
    """Tool description."""
    return result

# tools/__init__.py
from .my_tool import my_tool
__all__ = ["web_search_tool", "my_tool"]

# teams/group_team.py
from tools import web_search_tool, my_tool

self.researcher = AssistantAgent(
    ...,
    tools=[web_search_tool, my_tool],
    ...
)
```

### Customizing Agent Behavior

Edit system messages in `teams/group_team.py`:

```python
self.code_writer = AssistantAgent(
    ...,
    system_message="Your custom instructions here...",
    ...
)
```

### Monitoring Execution

Enable detailed logging:

```python
# In main.py or your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

## References

- [Implementation Specification](../implementation_spec.md)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [AutoGen AgentChat](https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/index.html)

## License

This project is for research and educational purposes.
