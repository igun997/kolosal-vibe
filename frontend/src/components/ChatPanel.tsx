import { useState, useRef, useEffect } from 'react';
import { useStore } from '../stores/store';
import { Send, Loader2 } from 'lucide-react';
import { ChatMessage } from './ChatMessage';

const SUGGESTIONS = [
  "Create a simple todo list app with add and delete functionality",
  "Build a calculator with a modern dark theme",
  "Make a weather dashboard with mock data",
  "Create a landing page for a SaaS product",
];

export function ChatPanel() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage, isGenerating } = useStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

    sendMessage(input);
    setInput('');
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isGenerating) return;
    sendMessage(suggestion);
  };

  return (
    <div className="flex flex-col h-full bg-kolosal-950">
      {/* Header */}
      <div className="p-4 border-b border-kolosal-800">
        <h2 className="text-lg font-semibold text-white">Chat</h2>
        <p className="text-sm text-kolosal-400">Describe what you want to build</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-kolosal-400 mt-4">
            <img
              src="/kolosal.svg"
              alt="Kolosal Vibes"
              className="w-12 h-12 mx-auto mb-4 invert opacity-50"
            />
            <p className="text-lg mb-2 text-white">Welcome to Kolosal Vibes!</p>
            <p className="text-sm mb-6">Describe an app and I'll build it for you.</p>
            <div className="space-y-2">
              {SUGGESTIONS.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="block w-full p-3 text-left text-sm text-kolosal-300 hover:bg-kolosal-900 hover:text-white rounded-lg border border-kolosal-800 transition-colors"
                >
                  "{suggestion}"
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isGenerating && messages[messages.length - 1]?.role === 'user' && (
          <div className="flex items-center text-kolosal-400 p-3">
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
            <span>Generating code...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-kolosal-800">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe what you want to build..."
            className="flex-1 bg-kolosal-900 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-accent-500 placeholder-kolosal-500 border border-kolosal-800"
            disabled={isGenerating}
          />
          <button
            type="submit"
            disabled={isGenerating || !input.trim()}
            className="bg-accent-600 hover:bg-accent-700 disabled:bg-kolosal-800 disabled:opacity-50 text-white rounded-lg px-4 py-3 transition-colors"
          >
            {isGenerating ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
