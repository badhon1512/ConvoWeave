"use client";

import { FormEvent, useEffect, useState } from "react";

import type {
  ActionItem,
  ConversationIntelligence,
  EvidenceClaim,
  GroundedAnswer,
} from "@/lib/types";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const fallbackError = "Could not generate conversation intelligence.";

export function ConversationIntelligencePanel({ conversationId }: { conversationId: string }) {
  const [intelligence, setIntelligence] = useState<ConversationIntelligence | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<GroundedAnswer | null>(null);
  const [questionError, setQuestionError] = useState("");
  const [isAnswering, setIsAnswering] = useState(false);

  useEffect(() => {
    let isCurrent = true;
    setIntelligence(null);
    setError("");
    setIsLoading(true);

    loadOrCreateIntelligence(conversationId)
      .then((result) => {
        if (isCurrent) setIntelligence(result);
      })
      .catch((reason: unknown) => {
        if (isCurrent) setError(reason instanceof Error ? reason.message : fallbackError);
      })
      .finally(() => {
        if (isCurrent) setIsLoading(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [conversationId, attempt]);

  useEffect(() => {
    setQuestion("");
    setAnswer(null);
    setQuestionError("");
  }, [conversationId]);

  async function askQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = question.trim();
    if (!value) return;

    setAnswer(null);
    setQuestionError("");
    setIsAnswering(true);
    try {
      const response = await fetch(
        `${apiUrl}/api/v1/conversations/${conversationId}/questions`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: value }),
        },
      );
      if (!response.ok) throw new Error(await errorDetail(response));
      setAnswer((await response.json()) as GroundedAnswer);
    } catch (reason) {
      setQuestionError(reason instanceof Error ? reason.message : fallbackError);
    } finally {
      setIsAnswering(false);
    }
  }

  return (
    <section className="intelligence-panel" aria-live="polite">
      <div className="panel-heading">
        <div>
          <span className="step">Insights</span>
          <h2>Conversation intelligence</h2>
        </div>
        {intelligence && <span className="status-dot">Citations checked</span>}
      </div>

      {isLoading && (
        <div className="processing-state intelligence-processing">
          <span className="spinner" />
          <div>
            <strong>Preparing conversation insights</strong>
            <p>Saved insights load instantly. New conversations are analyzed once.</p>
          </div>
        </div>
      )}

      {error && (
        <div className="intelligence-start">
          <p className="error-message">{error}</p>
          <button type="button" onClick={() => setAttempt((value) => value + 1)}>
            Try again
          </button>
        </div>
      )}

      {intelligence && (
        <div className="intelligence-result">
          <article className="overview-card">
            <span>Overview</span>
            <p>{intelligence.overview.text}</p>
            <Citations turns={intelligence.overview.turn_sequences} />
          </article>
          <div className="insight-grid">
            <ClaimSection title="Key points" items={intelligence.key_points} />
            <ClaimSection title="Decisions" items={intelligence.decisions} />
            <ActionSection items={intelligence.action_items} />
            <ClaimSection title="Risks" items={intelligence.risks} />
            <ClaimSection title="Open questions" items={intelligence.open_questions} />
          </div>
        </div>
      )}

      <section className="question-panel">
        <div>
          <span className="step">Grounded Q&amp;A</span>
          <h3>Ask this conversation</h3>
          <p>Answers use only the transcript and link back to supporting turns.</p>
        </div>
        <form onSubmit={askQuestion}>
          <input
            value={question}
            minLength={2}
            maxLength={500}
            placeholder="What was decided, and who owns the next action?"
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button type="submit" disabled={isAnswering || question.trim().length < 2}>
            {isAnswering ? "Finding evidence..." : "Ask"}
          </button>
        </form>
        {questionError && <p className="error-message">{questionError}</p>}
        {answer && (
          <article className={`answer-card ${answer.supported ? "" : "unsupported"}`}>
            <strong>{answer.supported ? "Answer" : "Not found in conversation"}</strong>
            <p>{answer.answer}</p>
            {answer.supported && <Citations turns={answer.turn_sequences} />}
          </article>
        )}
      </section>
    </section>
  );
}

const pendingRequests = new Map<string, Promise<ConversationIntelligence>>();

function loadOrCreateIntelligence(conversationId: string) {
  const pending = pendingRequests.get(conversationId);
  if (pending) return pending;

  const request = fetchOrCreateIntelligence(conversationId).finally(() => {
    pendingRequests.delete(conversationId);
  });
  pendingRequests.set(conversationId, request);
  return request;
}

async function fetchOrCreateIntelligence(
  conversationId: string,
): Promise<ConversationIntelligence> {
  const endpoint = `${apiUrl}/api/v1/conversations/${conversationId}/intelligence`;
  const saved = await fetch(endpoint);
  if (saved.ok) return (await saved.json()) as ConversationIntelligence;
  if (saved.status !== 404) throw new Error(await errorDetail(saved));

  const created = await fetch(endpoint, { method: "POST" });
  if (!created.ok) throw new Error(await errorDetail(created));
  return (await created.json()) as ConversationIntelligence;
}

async function errorDetail(response: Response) {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    return typeof payload.detail === "string" ? payload.detail : fallbackError;
  } catch {
    return fallbackError;
  }
}

function ClaimSection({ title, items }: { title: string; items: EvidenceClaim[] }) {
  return (
    <section className="insight-section">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="no-insights">Nothing supported by the transcript.</p>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={`${title}-${index}`}>
              <p>{item.text}</p>
              <Citations turns={item.turn_sequences} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function ActionSection({ items }: { items: ActionItem[] }) {
  return (
    <section className="insight-section">
      <h3>Action items</h3>
      {items.length === 0 ? (
        <p className="no-insights">No action items found.</p>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={`action-${index}`}>
              <p>{item.text}</p>
              {(item.owner || item.due_date) && (
                <small>{[item.owner, item.due_date].filter(Boolean).join(" - ")}</small>
              )}
              <Citations turns={item.turn_sequences} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function Citations({ turns }: { turns: number[] }) {
  return (
    <div className="citations">
      {turns.map((turn) => (
        <button
          type="button"
          key={turn}
          onClick={() =>
            document.getElementById(`turn-${turn}`)?.scrollIntoView({ behavior: "smooth" })
          }
        >
          Turn {turn}
        </button>
      ))}
    </div>
  );
}
