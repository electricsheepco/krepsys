import { Bookmark } from 'lucide-react';
import { useArticles } from '../hooks/useArticles';

const C = {
  bg:       '#f5efe4',
  border:   '#ddd4c0',
  header:   '#2a1e10',
  badge:    '#c8b898',
  badgeBg:  '#e8dfc8',
  unread:   '#1e1408',   /* strong dark brown for unread */
  read:     '#8a7860',
  date:     '#9a8870',
  dot:      '#c8762a',
  selected: '#e4d8c0',
};

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffMins < 60) return `${diffMins}m`;
  if (diffHours < 24) return `${diffHours}h`;
  if (diffDays < 7) return `${diffDays}d`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function ArticleList({ filters, selectedArticle, onSelectArticle }) {
  const { data: articles, isLoading, error } = useArticles(filters);

  return (
    <div
      className="w-80 flex flex-col h-screen flex-shrink-0"
      style={{ background: C.bg, borderRight: `1px solid ${C.border}` }}
    >
      {/* Header */}
      <div
        className="px-4 py-[13px] flex items-center justify-between flex-shrink-0"
        style={{ borderBottom: `1px solid ${C.border}` }}
      >
        <h2 className="text-[14px] font-bold" style={{ color: C.header }}>
          Articles
        </h2>
        {articles && (
          <span
            className="text-[11px] font-semibold px-2 py-0.5 rounded-md"
            style={{ background: C.badgeBg, color: C.badge }}
          >
            {articles.length}
          </span>
        )}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-3 space-y-2">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="p-3 rounded-xl" style={{ background: C.badgeBg }}>
                <div className="shimmer h-4 rounded-md w-3/4 mb-2" />
                <div className="shimmer h-3 rounded-md w-1/4" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="p-4 text-[13px] font-medium" style={{ color: '#c04030' }}>
            Error: {error.message}
          </div>
        ) : articles?.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-[13px] font-medium" style={{ color: C.read }}>No articles found</p>
          </div>
        ) : (
          <div key={JSON.stringify(filters)}>
            {articles?.map((article, i) => (
              <button
                key={article.id}
                onClick={() => onSelectArticle(article.id)}
                className={`article-row w-full text-left px-4 py-4 animate-fade-slide-up ${
                  selectedArticle === article.id ? 'selected' : ''
                }`}
                style={{
                  borderBottom: `1px solid ${C.border}`,
                  animationDelay: `${Math.min(i * 0.03, 0.3)}s`,
                }}
              >
                <div className="flex items-start justify-between gap-2">
                  <p
                    className="text-[13px] leading-snug flex-1"
                    style={{
                      color: article.is_read ? C.read : C.unread,
                      fontWeight: article.is_read ? 400 : 600,
                    }}
                  >
                    {article.title}
                  </p>
                  {!article.is_read && (
                    <div
                      className="w-2 h-2 rounded-full flex-shrink-0 mt-1"
                      style={{ background: C.dot }}
                    />
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-[11px] font-medium" style={{ color: C.date }}>
                    {formatDate(article.published_at || article.fetched_at)}
                  </span>
                  {article.is_saved && (
                    <Bookmark size={11} style={{ color: C.dot }} fill={C.dot} />
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
