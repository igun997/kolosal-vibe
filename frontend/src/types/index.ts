export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: string[];
}

export interface FileInfo {
  path: string;
  name: string;
  content?: string;
}

export interface Session {
  id: string;
  status: 'active' | 'loading' | 'error';
  previewUrl: string | null;
  previewToken: string | null;
  files: string[];
}

export interface PreviewData {
  url: string;
  token: string | null;
}

export interface CodeFile {
  filename: string;
  code: string;
}

export interface WebSocketMessage {
  type: 'chat' | 'update_code' | 'set_model';
  prompt?: string;
  path?: string;
  content?: string;
  model?: string;
}

export interface StreamResponse {
  type: 'token' | 'code' | 'preview' | 'complete' | 'error' | 'model_changed';
  content: string | CodeFile | PreviewData | { files: string[] } | { model: string };
}

export interface AIModel {
  id: string;
  name: string;
  context_size: number;
}
