import { useEffect, useState } from 'react';
import { useStore } from './stores/store';
import { Layout } from './components/Layout';
import { ChatPanel } from './components/ChatPanel';
import { PreviewPanel } from './components/PreviewPanel';

export default function App() {
  const { session, isConnecting, error, createSession, clearError, fetchModels } = useStore();
  const isLoadingModels = useStore((state) => state.isLoadingModels);
  const [modelsLoaded, setModelsLoaded] = useState(false);

  // Fetch models on mount
  useEffect(() => {
    fetchModels().then(() => setModelsLoaded(true));
  }, [fetchModels]);

  // Create session after models load attempt (even if it fails, use default model)
  useEffect(() => {
    if (!session && !isConnecting && modelsLoaded) {
      createSession();
    }
  }, [session, isConnecting, createSession, modelsLoaded]);

  if (isLoadingModels || isConnecting || !session) {
    return (
      <div className="flex items-center justify-center h-screen bg-kolosal-950 text-white">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <img
              src="/kolosal.svg"
              alt="Kolosal Vibes"
              className="w-16 h-16 invert animate-pulse"
            />
          </div>
          <h1 className="text-2xl font-bold mb-2 bg-gradient-to-r from-white to-kolosal-300 bg-clip-text text-transparent">
            Kolosal Vibes
          </h1>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-500 mx-auto mb-4 mt-6"></div>
          <p className="text-lg text-kolosal-200">
            {isLoadingModels ? 'Loading AI models...' : 'Initializing sandbox...'}
          </p>
          <p className="text-sm text-kolosal-400 mt-2">This may take a few seconds</p>
          {error && (
            <p className="text-sm text-red-400 mt-4">{error}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <Layout>
      {error && (
        <div className="absolute top-16 left-1/2 transform -translate-x-1/2 z-50 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
          <span>{error}</span>
          <button
            onClick={clearError}
            className="ml-2 hover:text-red-200"
          >
            &times;
          </button>
        </div>
      )}
      <div className="flex h-full">
        {/* Chat Panel - Left */}
        <div className="w-[400px] min-w-[350px] border-r border-kolosal-800 flex flex-col">
          <ChatPanel />
        </div>

        {/* Preview Panel - Right (takes remaining space) */}
        <div className="flex-1 flex flex-col">
          <PreviewPanel />
        </div>
      </div>
    </Layout>
  );
}
