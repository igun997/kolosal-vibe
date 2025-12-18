import { useRef, useState, useEffect } from 'react';
import { useStore } from '../stores/store';
import { RefreshCw, ExternalLink, Monitor, Smartphone, Tablet, Loader2 } from 'lucide-react';

type ViewportSize = 'desktop' | 'tablet' | 'mobile';

const viewportSizes: Record<ViewportSize, { width: string; icon: typeof Monitor }> = {
  desktop: { width: '100%', icon: Monitor },
  tablet: { width: '768px', icon: Tablet },
  mobile: { width: '375px', icon: Smartphone }
};

export function PreviewPanel() {
  const { session, isGenerating, previewVersion } = useStore();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [viewport, setViewport] = useState<ViewportSize>('desktop');

  // Preview URL is now our proxy endpoint - no token needed
  const fullUrl = session?.previewUrl || null;

  // Auto-reload iframe when preview version changes (new code deployed)
  useEffect(() => {
    if (iframeRef.current && fullUrl && previewVersion > 0) {
      // Add cache-busting parameter to force reload
      iframeRef.current.src = `${fullUrl}?v=${previewVersion}`;
    }
  }, [previewVersion, fullUrl]);

  const handleRefresh = () => {
    if (iframeRef.current && fullUrl) {
      iframeRef.current.src = fullUrl;
    }
  };

  const handleOpenExternal = () => {
    if (fullUrl) {
      window.open(fullUrl, '_blank');
    }
  };

  return (
    <div className="flex flex-col h-full bg-kolosal-950">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-kolosal-800">
        <div className="flex items-center space-x-4">
          <h3 className="text-sm font-medium text-white">Preview</h3>

          {/* Viewport toggles */}
          <div className="flex items-center space-x-1 bg-kolosal-900 rounded-lg p-1">
            {(Object.entries(viewportSizes) as [ViewportSize, { width: string; icon: typeof Monitor }][]).map(([size, { icon: Icon }]) => (
              <button
                key={size}
                onClick={() => setViewport(size)}
                className={`p-1.5 rounded transition-colors ${
                  viewport === size
                    ? 'bg-accent-600 text-white'
                    : 'text-kolosal-400 hover:text-white'
                }`}
                title={size.charAt(0).toUpperCase() + size.slice(1)}
              >
                <Icon className="w-4 h-4" />
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={handleRefresh}
            disabled={!fullUrl}
            className="p-2 text-kolosal-400 hover:text-white hover:bg-kolosal-900 disabled:opacity-50 disabled:hover:bg-transparent disabled:hover:text-kolosal-400 rounded transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleOpenExternal}
            disabled={!fullUrl}
            className="p-2 text-kolosal-400 hover:text-white hover:bg-kolosal-900 disabled:opacity-50 disabled:hover:bg-transparent disabled:hover:text-kolosal-400 rounded transition-colors"
            title="Open in new tab"
          >
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Preview iframe */}
      <div className="flex-1 bg-kolosal-900 flex items-start justify-center p-6 overflow-auto">
        {fullUrl ? (
          <div
            style={{ width: viewportSizes[viewport].width, maxWidth: '100%' }}
            className="h-full bg-white shadow-2xl rounded-xl overflow-hidden transition-all duration-300 border border-kolosal-700"
          >
            <iframe
              ref={iframeRef}
              src={fullUrl}
              className="w-full h-full border-0"
              title="Preview"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full w-full">
            <div className="text-center">
              {isGenerating ? (
                <>
                  <Loader2 className="w-16 h-16 mx-auto mb-4 text-accent-500 animate-spin" />
                  <p className="text-lg text-kolosal-200">Generating your app...</p>
                  <p className="text-sm text-kolosal-500 mt-2">This will appear here when ready</p>
                </>
              ) : (
                <>
                  <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-kolosal-800 flex items-center justify-center">
                    <Monitor className="w-12 h-12 text-kolosal-600" />
                  </div>
                  <p className="text-xl text-kolosal-200 font-medium">No preview yet</p>
                  <p className="text-sm text-kolosal-500 mt-2 max-w-xs">
                    Describe what you want to build in the chat and your app will appear here
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
