import { Message } from '../types';
import { User, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessageProps {
  message: Message;
}

// Remove code blocks from content for display
function stripCodeBlocks(content: string): string {
  // Remove ```filename.ext ... ``` blocks
  let cleaned = content.replace(/```[\w.]+\s*\n[\s\S]*?```/g, '');
  // Remove ```language ... ``` blocks
  cleaned = cleaned.replace(/```\w*\s*\n[\s\S]*?```/g, '');
  // Clean up excessive newlines
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n').trim();
  return cleaned;
}

// Check if original content had code blocks
function hasCodeBlocks(content: string): boolean {
  return /```[\s\S]*?```/.test(content);
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  // For assistant messages, strip code blocks
  const displayContent = isUser ? message.content : stripCodeBlocks(message.content);
  const hadCode = !isUser && hasCodeBlocks(message.content);

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-accent-600' : 'bg-kolosal-700'
      }`}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <img src="/kolosal.svg" alt="Kolosal" className="w-4 h-4 invert" />
        )}
      </div>
      <div className={`flex-1 min-w-0 ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block max-w-full p-3 rounded-2xl ${
          isUser
            ? 'bg-accent-600 text-white'
            : 'bg-kolosal-900 text-kolosal-100'
        }`}>
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <div className="text-sm space-y-2">
              {displayContent ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Hide code blocks completely
                    pre: () => null,
                    code: ({ children, className }) => {
                      // Only show inline code
                      if (!className) {
                        return (
                          <code className="bg-kolosal-800 px-1.5 py-0.5 rounded text-xs">
                            {children}
                          </code>
                        );
                      }
                      return null;
                    },
                    // Style links
                    a: ({ href, children }) => (
                      <a href={href} className="text-accent-400 hover:underline" target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    ),
                    // Style lists - prevent overflow
                    ul: ({ children }) => (
                      <ul className="list-disc ml-4 space-y-1">{children}</ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal ml-4 space-y-1">{children}</ol>
                    ),
                    li: ({ children }) => (
                      <li className="break-words">{children}</li>
                    ),
                    // Style paragraphs
                    p: ({ children }) => (
                      <p className="break-words leading-relaxed">{children}</p>
                    ),
                    // Style strong/bold
                    strong: ({ children }) => (
                      <strong className="font-semibold text-white">{children}</strong>
                    ),
                  }}
                >
                  {displayContent}
                </ReactMarkdown>
              ) : null}

              {/* Show deployment indicator if code was generated */}
              {hadCode && (
                <div className="flex items-center gap-2 text-accent-400 text-xs mt-2 pt-2 border-t border-kolosal-800">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Code deployed to preview</span>
                </div>
              )}
            </div>
          )}
        </div>
        <p className="text-xs text-kolosal-500 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
