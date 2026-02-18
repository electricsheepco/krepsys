import { useArticles } from '../hooks/useArticles';

export default function ArticleList({ filters, selectedArticle, onSelectArticle }) {
  const { data: articles, isLoading, error } = useArticles(filters);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="w-96 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Articles</h2>
        {articles && (
          <p className="text-sm text-gray-500 mt-1">{articles.length} articles</p>
        )}
      </div>

      {/* Article List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="p-4 border-b">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="p-4 text-red-600">
            Error loading articles: {error.message}
          </div>
        ) : articles?.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p>No articles found</p>
          </div>
        ) : (
          <div>
            {articles?.map(article => (
              <button
                key={article.id}
                onClick={() => onSelectArticle(article.id)}
                className={`w-full text-left p-4 border-b border-gray-100 hover:bg-gray-50 ${
                  selectedArticle === article.id ? 'bg-blue-50' : ''
                } ${!article.is_read ? 'font-medium' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <h3 className={`text-sm ${!article.is_read ? 'text-gray-900' : 'text-gray-600'}`}>
                    {article.title}
                  </h3>
                  {!article.is_read && (
                    <span className="ml-2 w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1"></span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-500">
                    {formatDate(article.published_at || article.fetched_at)}
                  </p>
                  {article.is_saved && (
                    <span className="text-xs text-blue-600">★</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
