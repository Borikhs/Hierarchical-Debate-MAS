"""
Phase 1: Parallel group execution orchestrator.
"""
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from autogen_ext.models.openai import OpenAIChatCompletionClient

from teams import GroupTeam
from config import GROUP_NAMES, CODING_DIR
from utils import TranscriptLogger


@dataclass
class GroupReport:
    """Report from a single group."""
    group_name: str
    messages: List
    solution: str
    stop_reason: str


class Phase1Orchestrator:
    """
    Orchestrates Phase 1: Parallel execution of 3 independent groups.

    Each group:
    - Works on the same task
    - Operates independently (no inter-group communication)
    - Generates its own solution/report
    """

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        work_dir: Path = CODING_DIR,
        logger: Optional[TranscriptLogger] = None
    ):
        self.model_client = model_client
        self.work_dir = work_dir
        self.logger = logger

        # Create 3 identical groups
        self.groups = [
            GroupTeam(
                group_name=name,
                model_client=model_client,
                work_dir=work_dir
            )
            for name in GROUP_NAMES
        ]

    async def run_group(self, group: GroupTeam, task: str) -> GroupReport:
        """
        Run a single group on the task.

        Args:
            group: The GroupTeam instance
            task: The task description

        Returns:
            GroupReport with the group's solution
        """
        print(f"\n{'='*60}")
        print(f"Starting {group.group_name}...")
        print(f"{'='*60}\n")

        try:
            result = await group.run(task=task)

            # Extract solution from the last message (Leader's report)
            solution = ""
            if result.messages:
                # Find the last message from the Leader
                for msg in reversed(result.messages):
                    if "Leader" in msg.source:
                        solution = msg.content
                        break

            report = GroupReport(
                group_name=group.group_name,
                messages=result.messages,
                solution=solution if solution else "No solution generated",
                stop_reason=result.stop_reason
            )

            print(f"\n{'='*60}")
            print(f"{group.group_name} completed!")
            print(f"Stop reason: {report.stop_reason}")
            print(f"{'='*60}\n")

            # Save transcript if logger is available
            if self.logger:
                transcript_path = self.logger.save_group_transcript(
                    group_name=group.group_name,
                    messages=result.messages,
                    metadata={
                        "stop_reason": result.stop_reason,
                        "message_count": len(result.messages)
                    }
                )
                print(f"[LOG] Transcript saved: {transcript_path}\n")

            return report

        except Exception as e:
            print(f"\n[ERROR] {group.group_name} failed: {e}\n")
            return GroupReport(
                group_name=group.group_name,
                messages=[],
                solution=f"ERROR: {str(e)}",
                stop_reason="error"
            )

    async def run_parallel(self, task: str) -> List[GroupReport]:
        """
        Run all 3 groups in parallel on the same task.

        Args:
            task: The task description

        Returns:
            List of GroupReport objects (one per group)
        """
        print(f"\n{'#'*60}")
        print("PHASE 1: PARALLEL GROUP EXECUTION")
        print(f"{'#'*60}")
        print(f"\nTask: {task}\n")
        print(f"Running {len(self.groups)} groups in parallel...\n")

        # Run all groups concurrently using asyncio.gather
        tasks = [self.run_group(group, task) for group in self.groups]
        reports = await asyncio.gather(*tasks)

        print(f"\n{'#'*60}")
        print("PHASE 1 COMPLETED")
        print(f"{'#'*60}\n")

        # Print summary
        for report in reports:
            print(f"\n{report.group_name} Report:")
            print(f"{'-'*60}")
            print(report.solution[:500])  # Print first 500 chars
            if len(report.solution) > 500:
                print("... (truncated)")
            print(f"{'-'*60}\n")

        return reports

    def cleanup(self):
        """Clean up all group resources."""
        for group in self.groups:
            group.cleanup()
