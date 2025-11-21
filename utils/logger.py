"""
Transcript logger for saving debate conversations.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class TranscriptLogger:
    """
    Logger for saving conversation transcripts to files.
    """

    def __init__(self, output_dir: Path = None):
        """
        Initialize the transcript logger.

        Args:
            output_dir: Directory to save transcripts (default: tmp/transcripts)
        """
        if output_dir is None:
            output_dir = Path("tmp/transcripts")

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / timestamp
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _serialize_content(self, content: Any) -> str:
        """
        Safely serialize message content to string format.
        Handles complex objects like FunctionCall that can't be JSON serialized.

        Args:
            content: The content to serialize

        Returns:
            String representation of the content
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, (list, tuple)):
            # Handle lists of objects (e.g., FunctionCall objects)
            return "\n".join(str(item) for item in content)
        else:
            # Convert any other object to string
            return str(content)

    def save_group_transcript(
        self,
        group_name: str,
        messages: List[Any],
        metadata: Dict[str, Any] = None
    ) -> Path:
        """
        Save a group's conversation transcript.

        Args:
            group_name: Name of the group
            messages: List of messages from the conversation
            metadata: Additional metadata to save

        Returns:
            Path to the saved file
        """
        filename = f"phase1_{group_name.lower()}.txt"
        filepath = self.session_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write(f"PHASE 1: {group_name} Internal Discussion\n")
            f.write("=" * 80 + "\n")
            f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if metadata:
                f.write(f"\nMetadata:\n")
                for key, value in metadata.items():
                    f.write(f"  {key}: {value}\n")

            f.write("\n" + "=" * 80 + "\n\n")

            # Write messages
            for i, msg in enumerate(messages, 1):
                speaker = getattr(msg, 'source', 'Unknown')
                content = getattr(msg, 'content', str(msg))

                f.write(f"[Message {i}] {speaker}\n")
                f.write("-" * 80 + "\n")
                f.write(f"{content}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write(f"End of {group_name} transcript\n")
            f.write("=" * 80 + "\n")

        # Also save as JSON for programmatic access
        json_filepath = self.session_dir / f"phase1_{group_name.lower()}.json"
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json_data = {
                "group_name": group_name,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
                "messages": [
                    {
                        "index": i,
                        "source": getattr(msg, 'source', 'Unknown'),
                        "content": self._serialize_content(getattr(msg, 'content', str(msg))),
                    }
                    for i, msg in enumerate(messages, 1)
                ]
            }
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)

        return filepath

    def save_debate_transcript(
        self,
        messages: List[Any],
        final_answer: str,
        metadata: Dict[str, Any] = None
    ) -> Path:
        """
        Save the Phase 2 debate transcript.

        Args:
            messages: List of messages from the debate
            final_answer: The final consensus answer
            metadata: Additional metadata to save

        Returns:
            Path to the saved file
        """
        filename = "phase2_leader_debate.txt"
        filepath = self.session_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write("PHASE 2: Leader Debate & Consensus\n")
            f.write("=" * 80 + "\n")
            f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if metadata:
                f.write(f"\nMetadata:\n")
                for key, value in metadata.items():
                    f.write(f"  {key}: {value}\n")

            f.write("\n" + "=" * 80 + "\n\n")

            # Write messages
            for i, msg in enumerate(messages, 1):
                speaker = getattr(msg, 'source', 'Unknown')
                content = getattr(msg, 'content', str(msg))

                f.write(f"[Message {i}] {speaker}\n")
                f.write("-" * 80 + "\n")
                f.write(f"{content}\n")
                f.write("\n")

            # Write final answer section
            f.write("=" * 80 + "\n")
            f.write("FINAL CONSENSUS\n")
            f.write("=" * 80 + "\n")
            f.write(f"{final_answer}\n")
            f.write("=" * 80 + "\n")

        # Also save as JSON
        json_filepath = self.session_dir / "phase2_leader_debate.json"
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json_data = {
                "phase": "phase2_debate",
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
                "messages": [
                    {
                        "index": i,
                        "source": getattr(msg, 'source', 'Unknown'),
                        "content": self._serialize_content(getattr(msg, 'content', str(msg))),
                    }
                    for i, msg in enumerate(messages, 1)
                ],
                "final_answer": final_answer
            }
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)

        return filepath

    def save_summary(
        self,
        task: str,
        phase1_reports: List[Any],
        phase2_result: Any
    ) -> Path:
        """
        Save an overall summary of the entire session.

        Args:
            task: The original task
            phase1_reports: Reports from Phase 1
            phase2_result: Result from Phase 2

        Returns:
            Path to the saved file
        """
        filename = "session_summary.txt"
        filepath = self.session_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MULTI-AGENT DEBATE SESSION SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Session Directory: {self.session_dir}\n")
            f.write("\n" + "=" * 80 + "\n\n")

            # Original task
            f.write("ORIGINAL TASK\n")
            f.write("-" * 80 + "\n")
            f.write(f"{task}\n\n")

            # Phase 1 summary
            f.write("=" * 80 + "\n")
            f.write("PHASE 1: GROUP REPORTS\n")
            f.write("=" * 80 + "\n\n")

            for report in phase1_reports:
                group_name = getattr(report, 'group_name', 'Unknown')
                solution = getattr(report, 'solution', 'No solution')
                stop_reason = getattr(report, 'stop_reason', 'Unknown')

                f.write(f"{group_name}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Stop Reason: {stop_reason}\n")
                f.write(f"Solution Preview: {solution[:200]}...\n")
                f.write(f"Full transcript: phase1_{group_name.lower()}.txt\n\n")

            # Phase 2 summary
            f.write("=" * 80 + "\n")
            f.write("PHASE 2: DEBATE & CONSENSUS\n")
            f.write("=" * 80 + "\n\n")

            consensus_reached = getattr(phase2_result, 'consensus_reached', False)
            final_answer = getattr(phase2_result, 'final_answer', 'No answer')

            f.write(f"Consensus Reached: {consensus_reached}\n")
            f.write(f"Full transcript: phase2_leader_debate.txt\n\n")

            f.write("FINAL ANSWER\n")
            f.write("-" * 80 + "\n")
            f.write(f"{final_answer}\n\n")

            f.write("=" * 80 + "\n")
            f.write("SESSION FILES\n")
            f.write("=" * 80 + "\n")
            f.write(f"Directory: {self.session_dir}/\n\n")
            f.write("Files:\n")
            f.write("  - session_summary.txt (this file)\n")
            f.write("  - phase1_group1.txt/.json\n")
            f.write("  - phase1_group2.txt/.json\n")
            f.write("  - phase1_group3.txt/.json\n")
            f.write("  - phase2_leader_debate.txt/.json\n")
            f.write("=" * 80 + "\n")

        return filepath

    def get_session_dir(self) -> Path:
        """Get the current session directory."""
        return self.session_dir
