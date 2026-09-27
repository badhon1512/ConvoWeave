"use client";

import { FormEvent, useEffect, useState } from "react";

import type { ConversationSummary, Transcription } from "@/lib/types";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function TranscriptionWorkspace() {
  const [audio, setAudio] = useState<File | null>(null);
  const [language, setLanguage] = useState("");
  const [speakerCount, setSpeakerCount] = useState("");
  const [transcription, setTranscription] = useState<Transcription | null>(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);

  async function loadConversations() {
    const response = await fetch(`${apiUrl}/api/v1/conversations`);
    if (response.ok) {
      setConversations((await response.json()) as ConversationSummary[]);
    }
  }

  useEffect(() => {
    void loadConversations();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!audio) {
      setError("Choose an audio file first.");
      return;
    }

    setError("");
    setTranscription(null);
    setIsSubmitting(true);

    const query = new URLSearchParams();
    if (language.trim()) query.set("language_code", language.trim());
    if (speakerCount) query.set("num_speakers", speakerCount);

    const body = new FormData();
    body.append("audio", audio);

    try {
      const response = await fetch(
        `${apiUrl}/api/v1/transcriptions?${query.toString()}`,
        { method: "POST", body },
      );
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail ?? "Transcription failed.");
      }

      setTranscription(payload as Transcription);
      await loadConversations();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Transcription failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function openConversation(transcriptId: string) {
    setError("");
    const response = await fetch(`${apiUrl}/api/v1/transcriptions/${transcriptId}`);
    if (!response.ok) {
      setError("Could not open the stored conversation.");
      return;
    }
    setTranscription((await response.json()) as Transcription);
  }

  return (
    <>
      <section className="workspace">
      <form className="upload-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <div>
            <span className="step">Step 1</span>
            <h2>Upload conversation</h2>
          </div>
          <span className="status-dot">Audio</span>
        </div>

        <label className="file-picker">
          <span>{audio ? audio.name : "Choose an audio file"}</span>
          <small>MP3, WAV, M4A, or another audio format</small>
          <input
            type="file"
            accept="audio/*"
            onChange={(event) => setAudio(event.target.files?.[0] ?? null)}
          />
        </label>

        <div className="field-grid">
          <label>
            Language <span>optional</span>
            <input
              value={language}
              maxLength={3}
              placeholder="eng"
              onChange={(event) => setLanguage(event.target.value)}
            />
          </label>
          <label>
            Speakers <span>optional</span>
            <input
              value={speakerCount}
              type="number"
              min="1"
              max="32"
              placeholder="Auto-detect"
              onChange={(event) => setSpeakerCount(event.target.value)}
            />
          </label>
        </div>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Separating speakers…" : "Create transcript"}
        </button>
        <p className="privacy-note">
          The API key stays on the server. The audio is sent to ElevenLabs for
          transcription.
        </p>
        {error && <p className="error-message">{error}</p>}
      </form>

      <section className="transcript-panel" aria-live="polite">
        <div className="panel-heading">
          <div>
            <span className="step">Step 2</span>
            <h2>Speaker conversation</h2>
          </div>
          {transcription && (
            <span className="status-dot">
              {transcription.speakers.length} speakers
            </span>
          )}
        </div>

        {!transcription && !isSubmitting && (
          <div className="empty-state">
            <div className="waveform" aria-hidden="true">
              {[18, 34, 54, 28, 66, 42, 72, 36, 58, 24].map((height, index) => (
                <i key={index} style={{ height }} />
              ))}
            </div>
            <p>Your speaker-labelled conversation will appear here.</p>
          </div>
        )}

        {isSubmitting && (
          <div className="processing-state">
            <span className="spinner" />
            <div>
              <strong>Listening to the conversation</strong>
              <p>Transcription can take a few minutes for longer audio.</p>
            </div>
          </div>
        )}

        {transcription && (
          <div className="transcript-result">
            {transcription.media_id && (
              <audio
                className="audio-player"
                controls
                preload="metadata"
                src={`${apiUrl}/api/v1/media/${transcription.media_id}`}
              />
            )}
            <div className="result-meta">
              <span>{transcription.turns.length} conversation turns</span>
              {transcription.language_code && (
                <span>Language: {transcription.language_code}</span>
              )}
            </div>
            {transcription.id && (
              <div className="speaker-editors">
                {transcription.speakers.map((speakerId) => (
                  <SpeakerEditor
                    key={speakerId}
                    transcriptionId={transcription.id!}
                    speakerId={speakerId}
                    initialName={transcription.speaker_names[speakerId] ?? ""}
                    onSaved={setTranscription}
                  />
                ))}
              </div>
            )}
            <ol className="turn-list">
              {transcription.turns.map((turn) => (
                <li key={turn.sequence} className="turn">
                  <div className="speaker-avatar">
                    {speakerInitial(turn.speaker_id)}
                  </div>
                  <div className="turn-content">
                    <div className="turn-heading">
                      <strong>
                        {turn.speaker_name ?? formatSpeaker(turn.speaker_id)}
                      </strong>
                      <time>{formatTime(turn.start)}</time>
                    </div>
                    <p>{turn.text}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        )}
      </section>
      </section>
      <section className="history-panel">
        <div className="panel-heading">
          <div>
            <span className="step">Library</span>
            <h2>Recent conversations</h2>
          </div>
          <span className="status-dot">{conversations.length} stored</span>
        </div>
        {conversations.length === 0 ? (
          <p className="history-empty">Stored conversations will appear here.</p>
        ) : (
          <ul className="conversation-list">
            {conversations.map((conversation) => (
              <li key={conversation.id}>
                <div>
                  <strong>{conversation.audio_filename ?? conversation.title}</strong>
                  <span>
                    {new Date(conversation.created_at).toLocaleString()} · {conversation.status}
                  </span>
                  <code>{conversation.id}</code>
                </div>
                <button
                  type="button"
                  disabled={!conversation.transcript_id}
                  onClick={() =>
                    conversation.transcript_id &&
                    void openConversation(conversation.transcript_id)
                  }
                >
                  {conversation.transcript_id ? "Open" : "Processing"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}

type SpeakerEditorProps = {
  transcriptionId: string;
  speakerId: string;
  initialName: string;
  onSaved: (transcription: Transcription) => void;
};

function SpeakerEditor({
  transcriptionId,
  speakerId,
  initialName,
  onSaved,
}: SpeakerEditorProps) {
  const [name, setName] = useState(initialName);
  const [isSaving, setIsSaving] = useState(false);

  async function saveName() {
    const displayName = name.trim();
    if (!displayName) return;

    setIsSaving(true);
    try {
      const response = await fetch(
        `${apiUrl}/api/v1/transcriptions/${transcriptionId}/speakers/${speakerId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ display_name: displayName }),
        },
      );
      if (!response.ok) throw new Error("Could not rename speaker.");
      onSaved((await response.json()) as Transcription);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="speaker-editor">
      <label htmlFor={`speaker-${speakerId}`}>{formatSpeaker(speakerId)}</label>
      <input
        id={`speaker-${speakerId}`}
        value={name}
        placeholder="Add name"
        maxLength={80}
        onChange={(event) => setName(event.target.value)}
      />
      <button type="button" disabled={!name.trim() || isSaving} onClick={saveName}>
        {isSaving ? "Saving" : "Save"}
      </button>
    </div>
  );
}

function formatSpeaker(speakerId: string) {
  const suffix = speakerId.match(/\d+$/)?.[0];
  return suffix ? `Speaker ${Number(suffix) + 1}` : "Unknown speaker";
}

function speakerInitial(speakerId: string) {
  const suffix = speakerId.match(/\d+$/)?.[0];
  return suffix ? String(Number(suffix) + 1) : "?";
}

function formatTime(totalSeconds: number) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
