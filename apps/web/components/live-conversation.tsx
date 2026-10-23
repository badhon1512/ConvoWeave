"use client";

import { useScribe } from "@elevenlabs/react";
import { useEffect, useRef, useState } from "react";

import { ConversationIntelligencePanel } from "@/components/conversation-intelligence";
import type { Transcription } from "@/lib/types";

export function LiveConversation({ apiUrl }: { apiUrl: string }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState("");
  const [transcription, setTranscription] = useState<Transcription | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startedAtRef = useRef(0);

  const scribe = useScribe({
    modelId: "scribe_v2_realtime",
    includeTimestamps: true,
    onError: (reason) => {
      setError(reason instanceof Error ? reason.message : "Live transcription failed.");
    },
  });

  useEffect(() => {
    if (!isRecording) return;
    const timer = window.setInterval(() => {
      setElapsedSeconds((seconds) => seconds + 1);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [isRecording]);

  useEffect(() => {
    return () => {
      scribe.disconnect();
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  async function startConversation() {
    setError("");
    setTranscription(null);
    setElapsedSeconds(0);
    scribe.clearTranscripts();

    try {
      const tokenResponse = await fetch(`${apiUrl}/api/v1/realtime/token`, {
        method: "POST",
      });
      const tokenPayload = (await tokenResponse.json()) as {
        token?: string;
        detail?: string;
      };
      if (!tokenResponse.ok || !tokenPayload.token) {
        throw new Error(tokenPayload.detail ?? "Could not start live transcription.");
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      streamRef.current = stream;
      chunksRef.current = [];

      const recorder = new MediaRecorder(stream, recordingOptions());
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.start(1000);
      recorderRef.current = recorder;

      await scribe.connect({
        token: tokenPayload.token,
        microphone: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      startedAtRef.current = Date.now();
      setIsRecording(true);
    } catch (reason) {
      stopMediaTracks();
      setError(
        reason instanceof Error ? reason.message : "Could not access the microphone.",
      );
    }
  }

  async function stopConversation() {
    setIsRecording(false);
    scribe.disconnect();

    try {
      const audio = await stopRecorder();
      stopMediaTracks();
      if (audio.size === 0) throw new Error("No audio was recorded.");

      setIsSaving(true);
      const extension = audio.type.includes("ogg") ? "ogg" : "webm";
      const body = new FormData();
      body.append(
        "audio",
        new File([audio], `live-conversation-${Date.now()}.${extension}`, {
          type: audio.type,
        }),
      );

      const response = await fetch(`${apiUrl}/api/v1/transcriptions`, {
        method: "POST",
        body,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "Could not save the conversation.");
      }
      setTranscription(payload as Transcription);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save the conversation.");
    } finally {
      setIsSaving(false);
    }
  }

  function stopRecorder() {
    return new Promise<Blob>((resolve) => {
      const recorder = recorderRef.current;
      if (!recorder || recorder.state === "inactive") {
        resolve(new Blob(chunksRef.current, { type: recorder?.mimeType || "audio/webm" }));
        return;
      }
      recorder.onstop = () => {
        resolve(new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" }));
      };
      recorder.stop();
    });
  }

  function stopMediaTracks() {
    const recorder = recorderRef.current;
    if (recorder?.state !== "inactive") recorder?.stop();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    recorderRef.current = null;
    streamRef.current = null;
  }

  const status = isSaving
    ? "Creating final transcript"
    : isRecording
      ? "Live"
      : scribe.status === "connecting"
        ? "Connecting"
        : "Ready";

  return (
    <section className="live-workspace">
      <aside className="live-controls">
        <div className="panel-heading">
          <div>
            <span className="step">Live session</span>
            <h2>Conversation controls</h2>
          </div>
          <span className={`status-dot ${isRecording ? "recording" : ""}`}>{status}</span>
        </div>

        <div className={`microphone-orb ${isRecording ? "active" : ""}`} aria-hidden="true">
          <span />
        </div>
        <strong className="session-time">{formatTime(elapsedSeconds)}</strong>
        <p className="session-help">
          {isRecording
            ? "Speak naturally. Confirmed phrases appear in the transcript."
            : "Start a session to stream and record your microphone."}
        </p>

        {!isRecording ? (
          <button
            type="button"
            disabled={isSaving || scribe.status === "connecting"}
            onClick={() => void startConversation()}
          >
            {scribe.status === "connecting" ? "Connecting..." : "Start conversation"}
          </button>
        ) : (
          <button className="stop-button" type="button" onClick={() => void stopConversation()}>
            Stop and save
          </button>
        )}

        <p className="privacy-note">
          Your API key stays on the server. Audio is recorded only after you start.
        </p>
        {error && <p className="error-message">{error}</p>}
      </aside>

      <section className="live-transcript" aria-live="polite">
        <div className="panel-heading">
          <div>
            <span className="step">Realtime</span>
            <h2>Live transcript</h2>
          </div>
          <span className="status-dot">{scribe.committedTranscripts.length} segments</span>
        </div>

        {scribe.committedTranscripts.length === 0 && !scribe.partialTranscript && (
          <div className="empty-state live-empty">
            <div className="waveform" aria-hidden="true">
              {[18, 34, 54, 28, 66, 42, 72, 36, 58, 24].map((height, index) => (
                <i key={index} style={{ height }} />
              ))}
            </div>
            <p>{isSaving ? "Processing the saved conversation..." : "Your words will appear here as you speak."}</p>
          </div>
        )}

        <ol className="live-segment-list">
          {scribe.committedTranscripts.map((segment) => (
            <li key={segment.id}>
              <time>
                {formatTime(
                  Math.max(0, Math.round((segment.timestamp - startedAtRef.current) / 1000)),
                )}
              </time>
              <p>{segment.text}</p>
            </li>
          ))}
          {scribe.partialTranscript && (
            <li className="partial-segment">
              <span>Listening</span>
              <p>{scribe.partialTranscript}</p>
            </li>
          )}
        </ol>

        {transcription && (
          <div className="final-transcript">
            <div className="final-heading">
              <div>
                <span className="step">Saved</span>
                <h3>Speaker-separated transcript</h3>
              </div>
              <span>{transcription.speakers.length} speakers</span>
            </div>
            <ol className="turn-list">
              {transcription.turns.map((turn) => (
                <li className="turn" key={turn.sequence} id={`turn-${turn.sequence}`}>
                  <div className="speaker-avatar">{speakerInitial(turn.speaker_id)}</div>
                  <div className="turn-content">
                    <div className="turn-heading">
                      <strong>{turn.speaker_name ?? formatSpeaker(turn.speaker_id)}</strong>
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
      {transcription?.conversation_id && (
        <div className="live-intelligence">
          <ConversationIntelligencePanel
            apiUrl={apiUrl}
            conversationId={transcription.conversation_id}
          />
        </div>
      )}
    </section>
  );
}

function recordingOptions(): MediaRecorderOptions | undefined {
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
    return { mimeType: "audio/webm;codecs=opus" };
  }
  if (MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")) {
    return { mimeType: "audio/ogg;codecs=opus" };
  }
  return undefined;
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
