"""
Main Multi-Agent Collaborative Debate System.

This system implements a two-phase approach:
- Phase 1: Three independent groups work in parallel
- Phase 2: Group leaders debate to reach consensus
"""
import asyncio
import os
from pathlib import Path
from typing import Optional

from autogen_ext.models.openai import OpenAIChatCompletionClient

from orchestration import Phase1Orchestrator, Phase2DebateOrchestrator
from config import MODEL_NAME, API_KEY, CODING_DIR
from utils import TranscriptLogger


class MultiAgentDebateSystem:
    """
    Main orchestrator for the multi-agent collaborative debate system.

    Architecture:
    1. Phase 1: 3 independent groups (each with 5 agents) work in parallel
    2. Phase 2: 3 group leaders debate to reach consensus
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        api_key: Optional[str] = None,
        work_dir: Path = CODING_DIR,
        enable_logging: bool = True,
        log_dir: Optional[Path] = None
    ):
        """
        Initialize the debate system.

        Args:
            model_name: OpenAI model name (e.g., "gpt-4o")
            api_key: OpenAI API key (defaults to env variable)
            work_dir: Working directory for code execution
            enable_logging: Whether to save transcripts to files
            log_dir: Directory for logs (default: tmp/transcripts)
        """
        # Setup API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = API_KEY or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        # Create model client
        self.model_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=self.api_key
        )

        # Create transcript logger
        self.logger = None
        if enable_logging:
            self.logger = TranscriptLogger(output_dir=log_dir)
            print(f"[LOG] Transcript logging enabled")
            print(f"[LOG] Session directory: {self.logger.get_session_dir()}\n")

        # Create orchestrators
        self.phase1 = Phase1Orchestrator(
            model_client=self.model_client,
            work_dir=work_dir,
            logger=self.logger
        )

        self.phase2 = Phase2DebateOrchestrator(
            model_client=self.model_client,
            logger=self.logger
        )

    async def run(self, task: str, verbose: bool = True):
        """
        Run the complete two-phase debate system.

        Args:
            task: The task/question to solve
            verbose: Whether to print detailed progress

        Returns:
            Dictionary with Phase 1 reports and Phase 2 consensus
        """
        if verbose:
            print("\n" + "="*80)
            print("MULTI-AGENT COLLABORATIVE DEBATE SYSTEM")
            print("="*80)
            print(f"\nTask: {task}\n")

        # Phase 1: Parallel group execution
        group_reports = await self.phase1.run_parallel(task)

        # Phase 2: Leader debate (pass original task to keep focus)
        debate_result = await self.phase2.run_debate(group_reports, original_task=task)

        # Print final result
        if verbose:
            print("\n" + "="*80)
            print("FINAL CONSENSUS")
            print("="*80)
            print(f"\n{debate_result.final_answer}\n")
            print("="*80 + "\n")

        # Save summary if logging is enabled
        if self.logger:
            summary_path = self.logger.save_summary(
                task=task,
                phase1_reports=group_reports,
                phase2_result=debate_result
            )
            print(f"[LOG] Session summary saved: {summary_path}")
            print(f"[LOG] All transcripts saved to: {self.logger.get_session_dir()}\n")

        return {
            "task": task,
            "phase1_reports": group_reports,
            "phase2_debate": debate_result,
            "final_answer": debate_result.final_answer,
            "log_directory": self.logger.get_session_dir() if self.logger else None
        }

    def cleanup(self):
        """Clean up resources."""
        self.phase1.cleanup()


async def main():
    """Example usage of the multi-agent debate system."""

    task ="""
    Question:
    Detailed analysis of sputum and systemic inflammation in asthma phenotypes: are paucigranulocytic asthmatics really non-inflammatory?
    
    Answer with one of: "yes", "no", or "maybe".
    """

    # Create system
    system = MultiAgentDebateSystem()

    try:
        # Run the system
        result = await system.run(task, verbose=True)

        # Save results (optional)
        print("\n[System] Debate complete!")
        print(f"[System] Phase 1: {len(result['phase1_reports'])} group reports generated")
        print(f"[System] Phase 2: Consensus reached = {result['phase2_debate'].consensus_reached}")

    finally:
        # Cleanup
        system.cleanup()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())