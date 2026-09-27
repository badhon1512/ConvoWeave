import { TranscriptionWorkspace } from "@/components/transcription-workspace";

export default function Home() {
  return (
    <main className="page-shell">
      <header className="hero">
        <span className="eyebrow">ConvoWeave</span>
        <h1>Hear every voice. Keep every detail.</h1>
        <p>
          Upload a conversation and receive a chronological transcript organized
          by speaker and timestamp.
        </p>
      </header>
      <TranscriptionWorkspace />
    </main>
  );
}

