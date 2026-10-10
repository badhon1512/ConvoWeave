import Link from "next/link";

import { LiveConversation } from "@/components/live-conversation";

export default function LivePage() {
  return (
    <main className="page-shell">
      <nav className="top-nav">
        <Link className="brand" href="/">ConvoWeave</Link>
        <div>
          <Link className="active" href="/live">Live</Link>
          <Link href="/">Upload</Link>
        </div>
      </nav>
      <header className="hero live-hero">
        <span className="eyebrow">Live conversation</span>
        <h1>Capture the moment while it happens.</h1>
        <p>
          Follow the conversation in realtime, then save the audio and create a
          speaker-separated transcript.
        </p>
      </header>
      <LiveConversation />
    </main>
  );
}
