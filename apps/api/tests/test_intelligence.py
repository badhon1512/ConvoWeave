import pytest

from app.schemas import (
    ActionItem,
    ConversationTurn,
    EvidenceClaim,
    IntelligenceDraft,
)
from app.services.intelligence import IntelligenceError, SummaryWorkflow


def test_summary_workflow_accepts_grounded_output() -> None:
    draft = _draft([1])
    result = SummaryWorkflow(lambda turns: draft).run([_turn()])

    assert result.overview.text == "The team agreed to ship on Friday."
    assert result.action_items[0].owner == "Alex"


def test_summary_workflow_rejects_unknown_turns() -> None:
    workflow = SummaryWorkflow(lambda turns: _draft([99]))

    with pytest.raises(IntelligenceError, match="unknown turns"):
        workflow.run([_turn()])


def _turn() -> ConversationTurn:
    return ConversationTurn(
        sequence=1,
        speaker_id="speaker_0",
        speaker_name="Alex",
        start=0,
        end=3,
        text="We will ship on Friday and I will prepare the release.",
        words=[],
    )


def _draft(turns: list[int]) -> IntelligenceDraft:
    claim = EvidenceClaim(
        text="The team agreed to ship on Friday.",
        turn_sequences=turns,
    )
    return IntelligenceDraft(
        overview=claim,
        key_points=[claim],
        decisions=[claim],
        action_items=[
            ActionItem(
                text="Prepare the release.",
                owner="Alex",
                due_date="Friday",
                turn_sequences=turns,
            )
        ],
        risks=[],
        open_questions=[],
    )
