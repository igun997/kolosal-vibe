import { useStore } from '../stores/store';
import { RotateCcw, ChevronDown } from 'lucide-react';

export function Toolbar() {
  const { session, models, selectedModel, setModel, isGenerating } = useStore();

  const handleNewSession = () => {
    if (confirm('Start a new session? Current work will be lost.')) {
      window.location.reload();
    }
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setModel(e.target.value);
  };

  return (
    <header className="flex items-center justify-between px-4 py-3 bg-kolosal-950 border-b border-kolosal-800">
      <div className="flex items-center space-x-3">
        <img
          src="/kolosal.svg"
          alt="Kolosal"
          className="w-7 h-7 invert"
        />
        <span className="text-xl font-bold bg-gradient-to-r from-white to-kolosal-300 bg-clip-text text-transparent">
          Kolosal Vibes
        </span>
        {session && (
          <span className="text-xs text-kolosal-400 bg-kolosal-900 px-2 py-1 rounded">
            {session.id.slice(0, 8)}...
          </span>
        )}
      </div>

      <div className="flex items-center space-x-3">
        {/* Model Selector */}
        <div className="relative">
          <select
            value={selectedModel || ''}
            onChange={handleModelChange}
            disabled={isGenerating}
            className="appearance-none bg-kolosal-900 text-white text-sm px-3 py-1.5 pr-8 rounded border border-kolosal-700 hover:border-kolosal-600 focus:outline-none focus:ring-2 focus:ring-accent-500 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-kolosal-400 pointer-events-none" />
        </div>

        <button
          onClick={handleNewSession}
          className="flex items-center px-3 py-1.5 text-sm bg-kolosal-900 hover:bg-kolosal-800 border border-kolosal-700 rounded transition-colors"
          title="New Session"
        >
          <RotateCcw className="w-4 h-4 mr-1.5" />
          New Project
        </button>
      </div>
    </header>
  );
}
