# ConvoWeave

### Agentic conversation intelligence for every important conversation

ConvoWeave is an agentic AI platform that transforms live and recorded multi-speaker conversations into structured, searchable, and actionable knowledge. It does more than transcribe: it understands the purpose of a conversation, runs specialized AI workflows, produces useful outputs, validates them against the transcript, and keeps every conclusion connected to its source evidence.

From a doctor-patient consultation to a hiring interview or team meeting, ConvoWeave turns hours of spoken information into reports, summaries, decisions, candidate evidence, risks, insights, action items, and grounded answers that people can review and use.

## The problem

Organizations create critical knowledge through conversations, but most of that knowledge becomes difficult to use as soon as the call ends.

- Recordings are slow to review and rarely revisited.
- Manual notes are incomplete, inconsistent, and influenced by the note-taker.
- Important decisions, symptoms, objections, risks, and commitments are easily missed.
- Information becomes fragmented across meetings, systems, and teams.
- Generic summaries often provide no evidence for their claims.
- Professionals repeatedly spend time converting conversations into reports, records, tasks, and follow-ups.
- Conventional chatbots may answer confidently without being grounded in what was actually said.

The result is lost context, duplicated work, slow decisions, weak accountability, and avoidable risk.

## How ConvoWeave solves it

ConvoWeave creates a trustworthy pipeline from raw speech to human-approved intelligence:

1. **Capture:** record a live conversation or upload existing audio.
2. **Structure:** identify speakers, words, turns, timestamps, and conversation metadata.
3. **Understand:** select the appropriate domain workflow and analyze the conversation's intent and content.
4. **Act:** generate summaries, reports, decisions, tasks, insights, and follow-up recommendations.
5. **Ground:** attach every important output to supporting transcript segments and timestamps.
6. **Review:** let authorized people correct, approve, reject, or regenerate the result.
7. **Reuse:** make the approved knowledge searchable, queryable, exportable, and available to connected systems.

Instead of treating transcription as the final product, ConvoWeave treats it as the evidence layer for an agentic knowledge system.

## What ConvoWeave delivers

- Live microphone transcription with immediate partial and confirmed text
- Recorded-audio upload for previously captured conversations
- Automatic speaker diarization and chronological conversation turns
- Word-level timestamps linked to the original recording
- Persistent audio, transcript, speaker, and conversation records
- Editable speaker identities and human-reviewed transcripts
- Evidence-backed summaries with direct links to supporting moments
- Structured report generation adapted to each domain
- Decisions, action items, owners, deadlines, risks, and follow-up extraction
- Cross-conversation trends, recurring themes, and operational insights
- Grounded conversational Q&A with transcript citations
- Search across conversations, speakers, topics, and organizations
- Domain-specific workflows for meetings, healthcare, support, sales, education, and research
- Multi-tenant workspaces, role-based access, consent, retention, and audit controls
- API-first integrations with communication, CRM, task, and record-management systems

## Product experience

### Live conversation

Start a live session from the browser and watch the transcript appear while people speak. ConvoWeave securely creates a temporary ElevenLabs token without exposing the permanent API key. The browser records the source audio at the same time.

When the session ends, ConvoWeave stores the recording and creates the canonical speaker-separated transcript used by the intelligence workflows.

### Recorded conversation

Upload an existing audio file, optionally provide language or speaker-count hints, and receive a structured transcript containing speakers, turns, timestamps, and word-level details.

### Conversation intelligence

Each completed conversation becomes a durable knowledge object. LangGraph coordinates specialized agents for classification, extraction, summarization, report generation, evidence retrieval, validation, and human review. Every important claim remains traceable to its supporting transcript segment and original audio.

### Search and Q&A

Users can search across the conversations they are authorized to access or ask natural-language questions. Answers are grounded in retrieved transcript evidence and include citations instead of unsupported model-generated claims.

Example questions include:

- "What did the patient say about the onset of symptoms?"
- "Which commitments from last week's meetings are still unresolved?"
- "What evidence did the candidate provide about leading a production migration?"
- "What objections appear most often in sales calls this quarter?"
- "Where in the recording was this decision made?"

## The agentic AI engine

ConvoWeave uses a stateful LangGraph workflow instead of a single prompt. Specialized agents collaborate over a shared conversation state while preserving deterministic boundaries around storage, permissions, schemas, and evidence.

### Workflow agents

| Agent | Responsibility |
|---|---|
| Conversation classifier | Determines the domain, conversation type, participants, and required workflow |
| Transcript quality agent | Detects gaps, uncertain passages, speaker inconsistencies, and low-confidence regions |
| Structured extraction agent | Extracts entities, topics, symptoms, competencies, decisions, risks, and commitments into typed schemas |
| Summary agent | Produces audience-appropriate executive, detailed, and domain-specific summaries |
| Report agent | Builds medical-note drafts, interview scorecards, meeting reports, support records, and other structured documents |
| Action agent | Identifies tasks, owners, deadlines, dependencies, and unresolved follow-ups |
| Insight agent | Finds themes, patterns, anomalies, sentiment shifts, and trends across authorized conversations |
| Retrieval agent | Finds the most relevant transcript segments and related conversations for a question |
| Answer agent | Produces grounded answers using only retrieved evidence |
| Validation agent | Checks completeness, schema compliance, citation support, contradictions, and unsupported claims |
| Review agent | Routes uncertain or high-impact outputs to the appropriate human reviewer |

### Agentic execution model

```text
Conversation completed
        |
        v
Classify domain and intent
        |
        v
Run domain extraction agents
        |
        +----------+-----------+------------+
        |          |           |            |
        v          v           v            v
    Summary      Report      Actions      Insights
        |          |           |            |
        +----------+-----------+------------+
                           |
                           v
               Retrieve supporting evidence
                           |
                           v
                Validate every major claim
                           |
                  +--------+--------+
                  |                 |
                  v                 v
             Human review      Approved output
```

Workflows are durable and resumable. Failed steps can retry without repeating completed work, checkpoints support human review, and each output records its model, prompt version, evidence, validation result, and approval state.

## Why ConvoWeave

Generic transcription products capture words. ConvoWeave converts those words into useful, verifiable work products while preserving meaning, evidence, ownership, and context.

The platform maintains four separate layers:

1. **Source evidence** - the original audio and immutable metadata
2. **Canonical record** - reviewed speakers, words, turns, and timestamps
3. **AI interpretation** - summaries, answers, decisions, and extracted actions
4. **Human approval** - corrections, verification, sign-off, and audit history

This separation prevents generated interpretations from silently replacing the source conversation.

## Architecture

```text
Browser and integrations
        |
        v
Next.js web application
        |
        v
FastAPI application API
        |
        +--------------------+
        |                    |
        v                    v
ElevenLabs Scribe      PostgreSQL
live and batch STT     conversations and metadata
        |                    |
        v                    v
Canonical transcript   pgvector retrieval index
        |                    |
        +----------+---------+
                   |
                   v
          LangGraph workflows
                   |
       +-----------+---------+----------+
       |           |         |          |
       v           v         v          v
   Summaries    Reports   Insights   Grounded Q&A
       |           |         |          |
       +-----------+---------+----------+
                   |
                   v
       Evidence and human review

Supporting services:
- Redis for queues, caching, and workflow coordination
- S3-compatible object storage for durable audio and exports
- Observability for logs, metrics, traces, cost, and model quality
```

### Core design principles

- **Evidence first:** generated outputs cite transcript segments and timestamps.
- **Provider isolation:** speech and model providers sit behind stable internal contracts.
- **Durable workflows:** long-running AI processes use checkpoints, retries, and idempotent steps.
- **Human control:** users can correct, approve, reject, and regenerate derived outputs.
- **Least privilege:** every retrieval and AI operation respects tenant and conversation access.
- **Domain extensibility:** specialized behavior is delivered through reusable domain packs.
- **Observable AI:** latency, token usage, cost, retrieval quality, and failures are measurable.

## Technology stack

| Area | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | FastAPI, Python |
| Realtime and batch speech | ElevenLabs Scribe |
| Agent orchestration | LangGraph |
| Primary database | PostgreSQL, SQLAlchemy, Alembic |
| Semantic retrieval | pgvector |
| Queue and cache | Redis |
| Media storage | S3-compatible object storage |
| Deployment | Docker and Docker Compose |
| Observability | Structured logs, metrics, traces, and evaluation datasets |

## Conversation lifecycle

```text
Capture or upload
      -> transcribe
      -> normalize
      -> separate speakers
      -> store canonical record
      -> run intelligence workflows
      -> validate evidence
      -> human review
      -> search, share, export, and integrate
```

Each conversation has a stable ID. Audio, transcripts, versions, speakers, turns, generated artifacts, citations, approvals, and audit events remain connected to that identity.

## Domain packs

ConvoWeave uses a shared conversation backbone with configurable domain packs.

| Domain | Specialized outputs |
|---|---|
| Team meetings | Decisions, owners, deadlines, blockers, and follow-ups |
| Healthcare | Clinician-reviewed encounter notes, symptoms, medications, instructions, risks, and follow-up drafts |
| Recruitment | Evidence-based interview scorecards, competency signals, candidate comparisons, and reviewer notes |
| Customer support | Issue, troubleshooting steps, resolution, sentiment, and escalation risk |
| Sales | Needs, objections, commitments, next steps, and CRM-ready notes |
| Education | Lecture structure, concepts, questions, study notes, and learning summaries |
| Research | Interview themes, evidence excerpts, entities, and cross-interview synthesis |

Domain packs change prompts, schemas, validation policies, retention rules, review requirements, and integrations without duplicating the core platform.

### Healthcare and medical reporting

ConvoWeave can convert a clinician-patient conversation into a structured draft containing the reason for visit, reported symptoms, history discussed, medications mentioned, assessment notes, patient instructions, and follow-up items. The report links important statements back to the transcript so a clinician can verify them quickly.

The system supports documentation; it does not independently diagnose, prescribe, or finalize a medical record. A qualified clinician reviews and approves every clinical output before use.

### Recruitment and interview intelligence

ConvoWeave turns interviews into consistent, evidence-backed scorecards. It extracts examples related to predefined competencies, summarizes candidate responses, highlights unanswered areas, and helps reviewers compare job-relevant evidence across interviews.

It does not autonomously select or reject candidates. Hiring teams define the criteria, review the cited evidence, consider appropriate context, and remain responsible for every employment decision. Sensitive or protected characteristics must not be used for ranking.

### Meetings and organizational memory

For team meetings, ConvoWeave creates concise and detailed summaries, captures decisions, assigns action items, identifies blockers, and tracks unresolved commitments across later conversations. Organization-wide insights reveal recurring risks, duplicated work, and themes that are difficult to see in a single meeting.

### Customer, sales, and research insights

Across support calls, sales conversations, and research interviews, the insight workflows aggregate recurring problems, objections, feature requests, sentiment changes, successful resolutions, and emerging themes. Teams can move from isolated anecdotes to evidence-linked patterns without manually reviewing every recording.

## Project structure

```text
conv-agent/
|-- apps/
|   |-- api/                    FastAPI service
|   |   |-- app/
|   |   |   |-- services/      Speech, media, persistence, and transcript logic
|   |   |   |-- config.py
|   |   |   |-- database.py
|   |   |   |-- main.py
|   |   |   |-- models.py
|   |   |   `-- schemas.py
|   |   |-- alembic/            Database migrations
|   |   |-- tests/
|   |   `-- Dockerfile
|   `-- web/                    Next.js application
|       |-- app/
|       |   `-- live/           Live conversation experience
|       |-- components/
|       |-- lib/
|       `-- Dockerfile
|-- docs/
|   `-- architecture/
|-- compose.yaml
|-- .env.example
`-- README.md
```

## Getting started

### Prerequisites

- Docker with Docker Compose
- An ElevenLabs API key

### 1. Configure the environment

Create the local environment file:

```shell
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Set the required values:

```env
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_MODEL_ID=scribe_v2
MAX_UPLOAD_MB=100
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

POSTGRES_DB=convoweave
POSTGRES_USER=convoweave
POSTGRES_PASSWORD=convoweave
DOCKER_DATABASE_URL=postgresql+psycopg://convoweave:convoweave@postgres:5432/convoweave
MEDIA_ROOT=/data/media
```

Never commit `.env` or expose the ElevenLabs key through a `NEXT_PUBLIC_` variable.

### 2. Start the platform

```shell
docker compose up --build
```

Open:

- Application: [http://localhost:3000](http://localhost:3000)
- Live conversation: [http://localhost:3000/live](http://localhost:3000/live)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

Browser microphone capture works on localhost during development. Production deployments must use HTTPS.

### 3. Stop the platform

```shell
docker compose down
```

Add `-v` only when you intentionally want to delete the PostgreSQL and media volumes.

## Using ConvoWeave

### Run a live session

1. Open `/live`.
2. Select **Start conversation** and allow microphone access.
3. Follow partial and confirmed text while speaking.
4. Select **Stop and save**.
5. Review the stored speaker-separated transcript.

The realtime transcript optimizes for immediacy. The transcript created after the session is the canonical record used for speaker attribution and downstream intelligence.

### Upload a recording

1. Open the main application.
2. Choose an audio file.
3. Optionally provide language and expected speaker count.
4. Create the transcript.
5. Review speakers, listen to the source audio, and assign speaker names.

## API reference

Interactive OpenAPI documentation is available at `/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health |
| `POST` | `/api/v1/realtime/token` | Create a temporary realtime Scribe token |
| `POST` | `/api/v1/transcriptions` | Upload, store, and transcribe audio |
| `GET` | `/api/v1/conversations` | List stored conversations |
| `GET` | `/api/v1/transcriptions/{id}` | Retrieve a structured transcript |
| `GET` | `/api/v1/media/{id}` | Stream stored source audio |
| `PATCH` | `/api/v1/transcriptions/{id}/speakers/{speaker_id}` | Assign a speaker name |

### Create a transcription

```shell
curl -X POST "http://localhost:8000/api/v1/transcriptions?num_speakers=2" \
  -F "audio=@conversation.mp3"
```

Optional query parameters:

| Parameter | Description |
|---|---|
| `language_code` | Two- or three-character language code such as `en` or `eng` |
| `num_speakers` | Expected number of speakers from 1 to 32 |

The response contains the conversation ID, media ID, detected language, speakers, complete text, chronological turns, timestamps, and word-level details.

## Persistence

PostgreSQL stores:

- Conversations and lifecycle status
- Transcript versions and full text
- Detected speakers and assigned display names
- Ordered turns with start and end timestamps
- Word-level transcript data
- Media metadata, content type, size, path, and SHA-256 checksum

Source audio is stored in a durable Docker volume for local deployments. Production installations use the storage abstraction with S3-compatible object storage.

## Testing and verification

Run the backend tests in Docker:

```shell
docker compose run --rm -e PYTHONPATH=/app api pytest -q
```

Build the frontend:

```shell
cd apps/web
npm install
npm run build
```

Check production dependencies:

```shell
npm audit --omit=dev
```

The test suite covers API health and configuration, transcript normalization, speaker-turn construction, punctuation, long pauses, persistence, and media storage.

## Security and governance

- Permanent provider credentials remain server-side.
- Browser sessions receive time-limited, single-use transcription tokens.
- Tenant and role checks protect conversations, search, exports, and AI workflows.
- Consent and retention policies can be configured per workspace and domain.
- Audit records capture access, changes, generated outputs, reviews, and deletions.
- Encryption protects network traffic and production storage.
- Evidence links and human approval support review of high-impact outputs.

Healthcare, legal, financial, and other regulated deployments still require the appropriate organizational policies, contracts, regional controls, validation, and independent compliance review.

## Documentation

- [Detailed product plan](PRODUCT_PLAN_DETAILED.md)
- [Compact product brief](PRODUCT_BRIEF_COMPACT.md)
- [Platform architecture decision](docs/architecture/ADR-0001-convoweave-platform-backbone.md)

## License

No open-source license has been assigned. All rights are reserved unless a license is added to the repository.
