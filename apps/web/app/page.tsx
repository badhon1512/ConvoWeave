import { TranscriptionWorkspace } from "@/components/transcription-workspace";
import Link from "next/link";

export default function Home() {
  return (
    <main className="page-shell">
      <nav className="top-nav">
        <Link className="brand" href="/">ConvoWeave</Link>
        <div>
          <Link href="/live">Live</Link>
          <Link className="active" href="/">Upload</Link>
        </div>
      </nav>
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
