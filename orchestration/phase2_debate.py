"""
Phase 2: Leader debate and consensus system.
"""
from typing import List, Optional
from dataclasses import dataclass

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from orchestration.phase1_parallel import GroupReport
from config import CONSENSUS_REACHED_KEYWORD, MAX_DEBATE_ROUNDS
from utils import TranscriptLogger


@dataclass
class DebateResult:
    """Result from the leader debate."""
    final_answer: str
    debate_messages: List
    consensus_reached: bool
    stop_reason: str


class Phase2DebateOrchestrator:
    """
    Orchestrates Phase 2: Leader debate and consensus building.

    After Phase 1, the 3 group leaders:
    - Present their group's findings
    - Debate different approaches
    - Reach consensus on the final answer
    """

    def __init__(self, model_client: OpenAIChatCompletionClient, logger: Optional[TranscriptLogger] = None):
        self.model_client = model_client
        self.logger = logger

    def _create_leader_agent(self, group_report: GroupReport) -> AssistantAgent:
        """
        Create a leader agent for the debate, initialized with their group's report.

        Args:
            group_report: The report from Phase 1

        Returns:
            AssistantAgent representing the group leader in debate
        """
        return AssistantAgent(
            name=f"{group_report.group_name}Leader",
            description=f"Leader representing {group_report.group_name}",
            model_client=self.model_client,
            system_message=f"""You are the leader of {group_report.group_name} in a multi-group debate.

Your group's findings from Phase 1:
{'-'*60}
{group_report.solution}
{'-'*60}

In this debate:
1. Present your group's approach and findings
2. Listen to other leaders' proposals
3. Identify agreements and disagreements
4. Debate politely and constructively
5. Be willing to revise your position if others have better reasoning
6. Work towards consensus

When all leaders agree on a final answer, support the consensus manager's decision.
"""
        )

    def _create_consensus_manager(self, original_task: str) -> AssistantAgent:
        """
        Create the consensus manager agent.

        Args:
            original_task: The original task that groups worked on

        Returns:
            AssistantAgent that manages the debate and synthesizes consensus
        """
        return AssistantAgent(
            name="ConsensusManager",
            description="Manages the debate and synthesizes final consensus",
            model_client=self.model_client,
            system_message=f"""You are the Consensus Manager for a multi-agent debate.

ORIGINAL TASK:
{'-'*60}
{original_task}
{'-'*60}

Your responsibilities:
1. Listen to all 3 group leaders present their findings about THE ORIGINAL TASK ABOVE
2. Identify areas of agreement and disagreement
3. Guide the discussion towards consensus ON THE ORIGINAL TASK
4. Synthesize the final answer when consensus emerges
5. KEEP THE DISCUSSION FOCUSED on the original task - if leaders go off-topic, remind them of the task

IMPORTANT: The debate must focus on solving the ORIGINAL TASK above. Do NOT discuss technical issues, logging problems, or meta-topics. Stay focused on answering the original question.

When to conclude:
- If all leaders agree on the answer to the ORIGINAL TASK → synthesize and conclude
- If leaders present different but valid approaches → identify the best one
- If there are errors in some solutions → help identify the correct one
- After sufficient debate rounds → make an executive decision
- If leaders are going off-topic → redirect them to the ORIGINAL TASK

To conclude the debate:
1. State the final answer clearly for the ORIGINAL TASK
2. Explain which groups' approaches were correct
3. Use the keyword '{CONSENSUS_REACHED_KEYWORD}' to end the debate

Be fair, objective, and focus on finding the correct answer to the ORIGINAL TASK.
"""
        )

    def _get_selector_prompt(self) -> str:
        """Get the selector prompt for the debate."""
        return """Select the next speaker in this multi-leader debate.

Available participants:
{roles}

Conversation history:
{history}

Selection rules:
1. Early rounds: Let each leader present their findings (round-robin style)
2. Middle rounds: Facilitate debate between leaders who disagree
3. Late rounds: Have ConsensusManager synthesize when convergence appears
4. If leaders are repeating points: Select ConsensusManager to conclude

Select from: {participants}
"""

    async def run_debate(self, group_reports: List[GroupReport], original_task: str) -> DebateResult:
        """
        Run the leader debate to reach consensus.

        Args:
            group_reports: Reports from Phase 1 (3 groups)
            original_task: The original task that groups worked on

        Returns:
            DebateResult with the final consensus answer
        """
        print(f"\n{'#'*60}")
        print("PHASE 2: LEADER DEBATE")
        print(f"{'#'*60}\n")

        # Create leader agents from group reports
        leaders = [
            self._create_leader_agent(report)
            for report in group_reports
        ]

        # Create consensus manager with original task
        consensus_manager = self._create_consensus_manager(original_task)

        # Create debate team
        debate_team = SelectorGroupChat(
            participants=[*leaders, consensus_manager],
            model_client=self.model_client,
            selector_prompt=self._get_selector_prompt(),
            termination_condition=(
                TextMentionTermination(CONSENSUS_REACHED_KEYWORD) |
                MaxMessageTermination(MAX_DEBATE_ROUNDS * len(leaders) + 5)
            )
        )

        # Prepare initial task for debate with clear task statement
        initial_prompt = f"""Welcome to the multi-group consensus debate.

ORIGINAL TASK:
{'-'*60}
{original_task}
{'-'*60}

Three groups have independently worked on this task.
Each group leader will now present their findings on THE TASK ABOVE.

After presentations, discuss and reach consensus on the final answer to THE ORIGINAL TASK.

Group leaders, please present your solutions to the task.
"""

        # Run debate
        print("Starting debate...\n")
        result = await debate_team.run(task=initial_prompt)

        # Extract final answer from ConsensusManager's last message
        final_answer = ""
        consensus_reached = CONSENSUS_REACHED_KEYWORD in result.stop_reason

        for msg in reversed(result.messages):
            if msg.source == "ConsensusManager":
                final_answer = msg.content
                break

        if not final_answer:
            final_answer = "No consensus reached. Debate inconclusive."

        debate_result = DebateResult(
            final_answer=final_answer,
            debate_messages=result.messages,
            consensus_reached=consensus_reached,
            stop_reason=result.stop_reason
        )

        print(f"\n{'#'*60}")
        print("PHASE 2 COMPLETED")
        print(f"{'#'*60}\n")
        print(f"Consensus reached: {consensus_reached}")
        print(f"Stop reason: {result.stop_reason}\n")

        # Save transcript if logger is available
        if self.logger:
            transcript_path = self.logger.save_debate_transcript(
                messages=result.messages,
                final_answer=final_answer,
                metadata={
                    "consensus_reached": consensus_reached,
                    "stop_reason": result.stop_reason,
                    "message_count": len(result.messages)
                }
            )
            print(f"[LOG] Debate transcript saved: {transcript_path}\n")

        return debate_result
