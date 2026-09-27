export type TranscriptWord = {
  text: string;
  start: number;
  end: number;
  speaker_id: string;
  type: string;
};

export type ConversationTurn = {
  sequence: number;
  speaker_id: string;
  speaker_name: string | null;
  start: number;
  end: number;
  text: string;
  words: TranscriptWord[];
};

export type Transcription = {
  id: string | null;
  conversation_id: string | null;
  media_id: string | null;
  audio_filename: string | null;
  language_code: string | null;
  language_probability: number | null;
  text: string;
  speakers: string[];
  speaker_names: Record<string, string>;
  turns: ConversationTurn[];
};

export type ConversationSummary = {
  id: string;
  title: string;
  status: string;
  created_at: string;
  media_id: string | null;
  audio_filename: string | null;
  transcript_id: string | null;
};
