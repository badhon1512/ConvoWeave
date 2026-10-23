import pytest

from app.schemas import (
    ActionItem,
    ConversationTurn,
    EvidenceClaim,
    GroundedAnswer,
    IntelligenceDraft,
)
from app.services.intelligence import (
    IntelligenceError,
    QuestionWorkflow,
    SummaryWorkflow,
)


def test_summary_workflow_accepts_grounded_output() -> None:
    draft = _draft([1])
    result = SummaryWorkflow(lambda turns: draft).run([_turn()])

    assert result.overview.text == "The team agreed to ship on Friday."
    assert result.action_items[0].owner == "Alex"


def test_summary_workflow_rejects_unknown_turns() -> None:
    workflow = SummaryWorkflow(lambda turns: _draft([99]))

    with pytest.raises(IntelligenceError, match="unknown turns"):
        workflow.run([_turn()])


def test_question_workflow_accepts_grounded_answer() -> None:
    answer = GroundedAnswer(
        answer="The team plans to ship on Friday.",
        supported=True,
        turn_sequences=[1],
    )

    result = QuestionWorkflow(lambda question, turns: answer).run(
        "When will the team ship?", [_turn()]
    )

    assert result.supported is True
    assert result.turn_sequences == [1]


def test_question_workflow_rejects_unsupported_citations() -> None:
    workflow = QuestionWorkflow(
        lambda question, turns: GroundedAnswer(
            answer="The conversation does not say.",
            supported=False,
            turn_sequences=[1],
        )
    )

    with pytest.raises(IntelligenceError, match="unsupported answer includes citations"):
        workflow.run("What is the budget?", [_turn()])


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
