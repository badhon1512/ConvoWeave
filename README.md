# ConvoWeave

### Agentic AI conversation intelligence for every important conversation

ConvoWeave is a multi-tenant conversation intelligence SaaS designed to transform multi-speaker audio into structured, searchable, and actionable knowledge.

It combines speaker-diarized transcription with evidence-backed AI workflows to produce transcripts, summaries, decisions, action items, and grounded Q&A for meetings, healthcare, customer support, sales, education, research, and other conversation-driven environments.

> **Current status:** Phase 1 implements the foundational audio-to-conversation workflow. Users can upload audio and receive a chronological transcript organized by speaker and timestamp.

## Why ConvoWeave?

Important information is often created during conversations and lost afterward. Recordings take too long to review, notes are inconsistent, and conventional AI summaries can be difficult to verify.

ConvoWeave is designed to preserve four distinct layers:

1. Original conversation
2. Speaker-labelled transcript
3. AI-generated interpretation
4. Human-approved record

This evidence-first approach ensures that future summaries, decisions, and answers can be traced back to the people and moments that support them.

## Current capabilities

- Audio upload through a responsive Next.js interface
- ElevenLabs Scribe speech-to-text integration
- Automatic speaker diarization
- Word-level timestamps
- Sequential conversation-turn generation
- Optional language and speaker-count hints
- Stable provider-neutral transcript format
- Audio type and size validation
- Dockerized frontend and backend
- Health checks and environment-based configuration

## Product direction

ConvoWeave is being designed as a reusable platform rather than a meeting-only transcription tool.

Planned product capabilities include:

- Evidence-backed summaries and grounded Q&A
- Decision, action-item, owner, and deadline extraction
- Durable LangGraph workflows with retries and checkpoints
- Human review, correction, and approval
- Search across authorized conversations
- Multi-tenant organizations, workspaces, and role-based access
- Consent, retention, audit, and deletion controls
- Domain packs for meetings, healthcare, support, sales, education, and research
- Integrations with communication, CRM, task, and record-management platforms

## Architecture

```text
Browser
   │
   ▼
Next.js web application
   │
   ▼
FastAPI application API
   │
   ▼
ElevenLabs Scribe
   │
   ▼
Provider response normalization
   │
   ▼
Chronological speaker conversation
```

The wider platform architecture introduces durable LangGraph workers, PostgreSQL, semantic retrieval, Redis, object storage, governance, and domain-specific workflow packs as later phases are implemented.

## Technology stack

| Area | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | FastAPI, Python |
| Speech intelligence | ElevenLabs Scribe |
| Agent orchestration | LangGraph — planned next phase |
| Deployment | Docker, Docker Compose |
| Future platform data | PostgreSQL, pgvector, Redis, S3-compatible storage |

## Project structure

```text
conv-agent/
├── apps/
│   ├── api/                   FastAPI service
│   │   ├── app/
│   │   │   ├── services/      ElevenLabs and transcript logic
│   │   │   ├── config.py
│   │   │   ├── main.py
│   │   │   └── schemas.py
│   │   ├── tests/
│   │   └── Dockerfile
│   └── web/                   Next.js application
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── Dockerfile
├── docs/
│   └── architecture/
├── compose.yaml
├── .env.example
└── README.md
```

## Getting started

### Prerequisites

- Docker with Docker Compose
- An ElevenLabs API key

### 1. Configure the environment

Create a local environment file from the provided template:

```shell
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Set your ElevenLabs key in `.env`:

```env
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_MODEL_ID=scribe_v2
MAX_UPLOAD_MB=100
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Never commit the `.env` file or expose the ElevenLabs key through a `NEXT_PUBLIC_` variable.

### 2. Start ConvoWeave

```shell
docker compose up --build
```

Open:

- Web application: `http://localhost:3000`
- API documentation: `http://localhost:8000/docs`
- API health check: `http://localhost:8000/health`

### 3. Stop the services

```shell
docker compose down
```

## API

### Create a transcription

```http
POST /api/v1/transcriptions
```

The request uses multipart form data with an `audio` file.

Optional query parameters:

| Parameter | Description |
|---|---|
| `language_code` | Two- or three-character language code, such as `en` or `eng` |
| `num_speakers` | Expected number of speakers from 1 to 32 |

Example:

```shell
curl -X POST "http://localhost:8000/api/v1/transcriptions?num_speakers=2" \
  -F "audio=@conversation.mp3"
```

The response contains detected speakers and chronological conversation turns:

```json
{
  "language_code": "en",
  "speakers": ["speaker_0", "speaker_1"],
  "turns": [
    {
      "sequence": 1,
      "speaker_id": "speaker_0",
      "start": 0.0,
      "end": 2.4,
      "text": "Good morning. How can I help you?"
    }
  ]
}
```

The actual response also contains word-level details for precise synchronization and future evidence linking.

## Testing

Run the API tests inside Docker:

```shell
docker compose run --rm api pytest
```

Build the frontend locally:

```shell
cd apps/web
npm install
npm run build
```

The existing tests cover transcript normalization, speaker-turn construction, punctuation, long pauses, health checks, and missing-provider configuration.

## Roadmap

### Phase 1 — Audio to conversation

- [x] Dockerized Next.js and FastAPI applications
- [x] Audio upload
- [x] ElevenLabs transcription
- [x] Speaker diarization
- [x] Sequential timestamped turns
- [x] Conversation interface

### Phase 2 — Durable conversation records

- [ ] PostgreSQL persistence
- [ ] S3-compatible media storage
- [ ] Background processing
- [ ] Transcript correction and speaker naming
- [ ] Versioned canonical transcripts

### Phase 3 — Agentic intelligence

- [ ] LangGraph processing workflows
- [ ] Evidence-backed summaries
- [ ] Decisions and action items
- [ ] Citation validation
- [ ] Human review and approval

### Phase 4 — SaaS platform

- [ ] Organizations and workspaces
- [ ] Role-based access
- [ ] Permission-aware search and Q&A
- [ ] Consent, retention, and audit controls
- [ ] Domain packs and external integrations

## Documentation

- [Detailed product plan](PRODUCT_PLAN_DETAILED.md)
- [Compact product brief](PRODUCT_BRIEF_COMPACT.md)
- [Platform architecture decision](docs/architecture/ADR-0001-convoweave-platform-backbone.md)

## Security

ConvoWeave is under active development and is not yet approved for clinical, legal, financial, or other regulated production use.

Do not upload sensitive or regulated conversations until the required consent, storage, access, retention, audit, contractual, and compliance controls have been implemented and independently reviewed.
