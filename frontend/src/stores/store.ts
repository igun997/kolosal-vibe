import { create } from 'zustand';
import { Message, Session, CodeFile, AIModel } from '../types';

const API_BASE = '/api';

interface AppState {
  session: Session | null;
  messages: Message[];
  isGenerating: boolean;
  isConnecting: boolean;
  error: string | null;
  ws: WebSocket | null;
  previewVersion: number;  // Increments on each preview update to trigger refresh
  models: AIModel[];
  selectedModel: string | null;
  isLoadingModels: boolean;

  // Actions
  fetchModels: () => Promise<void>;
  setModel: (modelId: string) => void;
  createSession: () => Promise<void>;
  sendMessage: (prompt: string) => void;
  clearError: () => void;
}

export const useStore = create<AppState>((set, get) => ({
  session: null,
  messages: [],
  isGenerating: false,
  isConnecting: false,
  error: null,
  ws: null,
  previewVersion: 0,
  models: [],
  selectedModel: null,
  isLoadingModels: false,

  fetchModels: async () => {
    set({ isLoadingModels: true });
    try {
      const response = await fetch(`${API_BASE}/models`);
      if (response.ok) {
        const models = await response.json();
        set({
          models,
          selectedModel: models[0]?.id || null,
          isLoadingModels: false
        });
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      set({ isLoadingModels: false });
    }
  },

  setModel: (modelId: string) => {
    const { ws, session } = get();
    set({ selectedModel: modelId });

    // If we have an active session, notify the backend
    if (ws && session && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'set_model',
        model: modelId
      }));
    }
  },

  createSession: async () => {
    const { selectedModel } = get();
    set({ isConnecting: true, error: null });

    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: selectedModel })
      });

      if (!response.ok) {
        throw new Error('Failed to create session');
      }

      const data = await response.json();

      // Connect WebSocket
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${window.location.host}/ws/${data.session_id}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        const state = get();

        switch (message.type) {
          case 'token': {
            // Update or create assistant message with streaming content
            const messages = [...state.messages];
            const lastMsg = messages[messages.length - 1];

            if (lastMsg?.role === 'assistant') {
              lastMsg.content += message.content;
              set({ messages: [...messages] });
            } else {
              messages.push({
                id: Date.now().toString(),
                role: 'assistant',
                content: message.content,
                timestamp: new Date()
              });
              set({ messages });
            }
            break;
          }

          case 'code': {
            // Files are synced to sandbox - we just acknowledge receipt
            const { filename } = message.content as CodeFile;
            console.log(`File synced to sandbox: ${filename}`);
            break;
          }

          case 'preview': {
            // Use our proxy URL instead of direct Daytona URL
            const { session, previewVersion } = get();
            if (session) {
              set({
                session: {
                  ...session,
                  // Point to our proxy endpoint which handles Daytona auth
                  previewUrl: `/api/proxy/${session.id}/`,
                  previewToken: null  // Not needed with proxy
                },
                // Increment to trigger auto-reload in PreviewPanel
                previewVersion: previewVersion + 1
              });
            }
            break;
          }

          case 'complete': {
            const { files } = message.content as { files: string[] };
            set((state) => ({
              isGenerating: false,
              session: state.session ? {
                ...state.session,
                files
              } : null
            }));
            break;
          }

          case 'error': {
            set({
              isGenerating: false,
              error: message.content as string
            });
            break;
          }

          case 'model_changed': {
            const { model } = message.content as { model: string };
            console.log(`Model changed to: ${model}`);
            break;
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        set({ error: 'WebSocket connection error' });
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
      };

      set({
        session: {
          id: data.session_id,
          status: 'active',
          previewUrl: null,
          previewToken: null,
          files: []
        },
        ws,
        isConnecting: false
      });

    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create session',
        isConnecting: false
      });
    }
  },

  sendMessage: (prompt: string) => {
    const { ws, session } = get();
    if (!ws || !session || ws.readyState !== WebSocket.OPEN) {
      set({ error: 'Not connected to server' });
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: prompt,
      timestamp: new Date()
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isGenerating: true,
      error: null
    }));

    // Send via WebSocket
    ws.send(JSON.stringify({
      type: 'chat',
      prompt
    }));
  },

  clearError: () => {
    set({ error: null });
  }
}));
