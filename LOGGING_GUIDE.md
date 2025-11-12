# Logging Guide

## Overview

The Multi-Agent Debate System automatically saves all conversations to files, making it easy to review what happened during execution.

## Quick Start

**Logging is enabled by default** - no configuration needed!

```python
from main import MultiAgentDebateSystem
import asyncio

async def main():
    system = MultiAgentDebateSystem()  # Logging enabled automatically
    result = await system.run(task="Your task here")

    print(f"Logs saved to: {result['log_directory']}")

asyncio.run(main())
```

## What Gets Logged

### 1. Phase 1: Group Transcripts (3 files)
- `phase1_group1.txt` - Complete conversation within Group 1
- `phase1_group2.txt` - Complete conversation within Group 2
- `phase1_group3.txt` - Complete conversation within Group 3

Each file contains:
- All messages between Leader, CodeWriter, CodeExecutor, Researcher, and Analyst
- Timestamps
- Stop reason
- Message count

### 2. Phase 2: Debate Transcript (1 file)
- `phase2_leader_debate.txt` - Leader debate and consensus process

Contains:
- All messages between the 3 leaders and Consensus Manager
- Final consensus decision
- Debate metadata

### 3. Session Summary (1 file)
- `session_summary.txt` - High-level overview

Contains:
- Original task
- Brief summary of each group's findings
- Consensus status
- Links to detailed transcripts

### 4. JSON Versions (for programmatic access)
- All `.txt` files also saved as `.json` for easy parsing

## Directory Structure

```
tmp/transcripts/
└── 20250110_143022/              # Timestamped session folder
    ├── session_summary.txt        # Overview
    ├── phase1_group1.txt          # Group 1 discussion
    ├── phase1_group1.json         # Group 1 (JSON)
    ├── phase1_group2.txt          # Group 2 discussion
    ├── phase1_group2.json         # Group 2 (JSON)
    ├── phase1_group3.txt          # Group 3 discussion
    ├── phase1_group3.json         # Group 3 (JSON)
    ├── phase2_leader_debate.txt   # Leader debate
    └── phase2_leader_debate.json  # Leader debate (JSON)
```

Each execution creates a **new timestamped folder**, so logs never overwrite each other.

## Example Log Content

### Phase 1 Group Transcript

```
================================================================================
PHASE 1: Group1 Internal Discussion
================================================================================
Saved: 2025-01-10 14:30:22

Metadata:
  stop_reason: Text 'REPORT_READY' mentioned
  message_count: 15

================================================================================

[Message 1] Group1Leader
--------------------------------------------------------------------------------
Let's solve this step by step. CodeWriter, please create a function to
calculate the 10th Fibonacci number.

[Message 2] Group1CodeWriter
--------------------------------------------------------------------------------
Here's a Python function to calculate Fibonacci numbers:

```python
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

result = fibonacci(10)
print(f"The 10th Fibonacci number is: {result}")
```

[Message 3] Group1CodeExecutor
--------------------------------------------------------------------------------
Exit code: 0
Output:
The 10th Fibonacci number is: 55

[Message 4] Group1Analyst
--------------------------------------------------------------------------------
The result is correct. The 10th Fibonacci number is indeed 55.
The sequence is: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55.

[Message 5] Group1Leader
--------------------------------------------------------------------------------
Excellent work team! Our analysis confirms the answer is 55.
REPORT_READY

================================================================================
End of Group1 transcript
================================================================================
```

### Phase 2 Debate Transcript

```
================================================================================
PHASE 2: Leader Debate & Consensus
================================================================================
Saved: 2025-01-10 14:31:45

Metadata:
  consensus_reached: True
  stop_reason: Text 'CONSENSUS_REACHED' mentioned
  message_count: 8

================================================================================

[Message 1] Group1Leader
--------------------------------------------------------------------------------
Our group calculated the 10th Fibonacci number using an iterative approach.
We found the answer to be 55.

[Message 2] Group2Leader
--------------------------------------------------------------------------------
We used a recursive implementation and also arrived at 55 as the answer.

[Message 3] Group3Leader
--------------------------------------------------------------------------------
Our team verified using a mathematical formula and confirmed: 55.

[Message 4] ConsensusManager
--------------------------------------------------------------------------------
Excellent! All three independent groups have reached the same conclusion
through different methods (iterative, recursive, and formula-based).

The 10th Fibonacci number is definitively 55.

CONSENSUS_REACHED

================================================================================
FINAL CONSENSUS
================================================================================
The 10th Fibonacci number is 55, verified by three independent teams using
different computational approaches. This high degree of agreement across
diverse methods provides strong confidence in the result.
================================================================================
```

## Configuration Options

### Disable Logging

```python
# Turn off logging completely
system = MultiAgentDebateSystem(enable_logging=False)
```

### Custom Log Directory

```python
from pathlib import Path

# Save logs to custom location
system = MultiAgentDebateSystem(log_dir=Path("my_research_logs"))
```

### Access Log Directory Programmatically

```python
result = await system.run(task="...")

if result['log_directory']:
    log_dir = result['log_directory']

    # Read summary
    with open(log_dir / "session_summary.txt") as f:
        print(f.read())

    # Read Group 1 transcript
    with open(log_dir / "phase1_group1.txt") as f:
        print(f.read())
```

### Parse JSON Logs

```python
import json

log_dir = result['log_directory']

# Parse Group 1 JSON
with open(log_dir / "phase1_group1.json") as f:
    data = json.load(f)

    print(f"Group: {data['group_name']}")
    print(f"Messages: {len(data['messages'])}")

    for msg in data['messages']:
        print(f"\n{msg['source']}:")
        print(msg['content'][:100] + "...")
```

## Use Cases

### 1. Debugging
Review exact agent conversations to understand what went wrong:

```bash
# Find the failed group
grep -r "ERROR" tmp/transcripts/20250110_143022/

# Read that group's transcript
cat tmp/transcripts/20250110_143022/phase1_group2.txt
```

### 2. Analysis
Compare how different groups approached the problem:

```bash
# Compare all group reports
diff phase1_group1.txt phase1_group2.txt
```

### 3. Research
Study multi-agent collaboration patterns:

```python
import json
from pathlib import Path

# Analyze message counts
for group_file in Path("tmp/transcripts/20250110_143022").glob("phase1_*.json"):
    with open(group_file) as f:
        data = json.load(f)
        print(f"{data['group_name']}: {len(data['messages'])} messages")
```

### 4. Quality Assurance
Verify that agents followed instructions:

```bash
# Check if CodeWriter actually wrote code
grep -A 10 "CodeWriter" phase1_group1.txt | grep "python"

# Check if Analyst validated results
grep "Analyst" phase1_group1.txt
```

### 5. Training Data
Logs can be used as training data for improving agent prompts:

```python
# Extract all successful problem-solving patterns
import json

successful_patterns = []
for session in Path("tmp/transcripts").iterdir():
    with open(session / "session_summary.txt") as f:
        if "consensus_reached: True" in f.read():
            successful_patterns.append(session)
```

## Tips

1. **Review logs after each run** - Helps understand agent behavior
2. **Compare different sessions** - See how approaches vary
3. **Archive important sessions** - Move to permanent storage
4. **Clean old logs periodically** - Can take up space
5. **Use JSON for analysis** - Easier to parse programmatically

## Log Retention

Logs are saved in `tmp/transcripts/` by default. Consider:

```bash
# Archive old logs
mkdir -p archives/
mv tmp/transcripts/2025* archives/

# Clean very old logs (optional)
find tmp/transcripts -type d -mtime +30 -exec rm -rf {} \;
```

## Troubleshooting

### "Permission denied" errors
```bash
# Ensure tmp directory is writable
chmod -R 755 tmp/
```

### Logs not being created
```python
# Check if logging is enabled
system = MultiAgentDebateSystem(enable_logging=True)  # Explicit

# Verify log directory
result = await system.run(task="...")
print(result['log_directory'])  # Should print a path
```

### Can't find logs
```bash
# Search for today's logs
find tmp/transcripts -name "*.txt" -mtime -1

# List all sessions
ls -lt tmp/transcripts/
```

## Summary

- ✅ Logging **enabled by default**
- ✅ **Timestamped folders** prevent overwriting
- ✅ **Both .txt and .json** formats
- ✅ Complete conversation history
- ✅ Easy to review and analyze
- ✅ Can be **disabled** if needed

For more information, see [README.md](README.md).
