from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from openai import OpenAI

from app.schemas import ConversationTurn, IntelligenceDraft


PROMPT_VERSION = "summary_v1"


class IntelligenceError(Exception):
    pass


class IntelligenceState(TypedDict):
    turns: list[ConversationTurn]
    draft: IntelligenceDraft | None
    validation_errors: list[str]


SummaryGenerator = Callable[[list[ConversationTurn]], IntelligenceDraft]


class OpenAISummaryGenerator:
    def __init__(
        self,
        api_key: str,
        model_id: str,
        timeout_seconds: float,
    ) -> None:
        self.model_id = model_id
        self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    def __call__(self, turns: list[ConversationTurn]) -> IntelligenceDraft:
        response = self.client.responses.parse(
            model=self.model_id,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You create factual conversation intelligence. Use only the "
                        "provided transcript. Every overview, key point, decision, action "
                        "item, risk, and open question must cite one or more supporting "
                        "turn sequence numbers. Return an empty list when a category has "
                        "no supporting evidence. Never invent people, decisions, owners, "
                        "deadlines, or facts."
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a structured summary of this conversation:\n\n"
                    + _format_turns(turns),
                },
            ],
            text_format=IntelligenceDraft,
        )
        if response.output_parsed is None:
            raise IntelligenceError("The model did not return a structured summary.")
        return response.output_parsed


class SummaryWorkflow:
    def __init__(self, generator: SummaryGenerator) -> None:
        self.generator = generator
        graph = StateGraph(IntelligenceState)
        graph.add_node("generate", self._generate)
        graph.add_node("validate", self._validate)
        graph.add_edge(START, "generate")
        graph.add_edge("generate", "validate")
        graph.add_edge("validate", END)
        self.graph = graph.compile()

    def run(self, turns: list[ConversationTurn]) -> IntelligenceDraft:
        try:
            result = self.graph.invoke(
                {"turns": turns, "draft": None, "validation_errors": []}
            )
        except IntelligenceError:
            raise
        except Exception as exc:
            raise IntelligenceError("Could not generate conversation intelligence.") from exc

        errors = result["validation_errors"]
        if errors:
            raise IntelligenceError("Summary validation failed: " + "; ".join(errors))
        draft = result["draft"]
        if draft is None:
            raise IntelligenceError("The workflow completed without a summary.")
        return draft

    def _generate(self, state: IntelligenceState) -> dict:
        return {"draft": self.generator(state["turns"])}

    def _validate(self, state: IntelligenceState) -> dict:
        draft = state["draft"]
        if draft is None:
            return {"validation_errors": ["Missing summary draft."]}
        valid_turns = {turn.sequence for turn in state["turns"]}
        errors: list[str] = []
        for label, references in _references(draft):
            invalid = sorted(set(references) - valid_turns)
            if invalid:
                errors.append(f"{label} cites unknown turns {invalid}")
        return {"validation_errors": errors}


def _references(draft: IntelligenceDraft):
    yield "overview", draft.overview.turn_sequences
    for field in ("key_points", "decisions", "action_items", "risks", "open_questions"):
        for index, item in enumerate(getattr(draft, field), start=1):
            yield f"{field}[{index}]", item.turn_sequences


def _format_turns(turns: list[ConversationTurn]) -> str:
    lines = []
    for turn in turns:
        speaker = turn.speaker_name or turn.speaker_id
        lines.append(
            f"[turn {turn.sequence} | {speaker} | {_time(turn.start)}-{_time(turn.end)}] "
            f"{turn.text}"
        )
    return "\n".join(lines)


def _time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining = int(seconds % 60)
    return f"{minutes}:{remaining:02d}"
