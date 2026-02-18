import { useArticle } from '../hooks/useArticles';
import { useUpdateArticle } from '../hooks/useArticles';
import { useEffect } from 'react';

export default function ArticleReader({ articleId }) {
  const { data: article, isLoading } = useArticle(articleId);
  const updateArticle = useUpdateArticle();

  // Mark as read when article is opened
  useEffect(() => {
    if (article && !article.is_read) {
      updateArticle.mutate({
        id: article.id,
        updates: { is_read: true }
      });
    }
  }, [article?.id]);

  const toggleSaved = () => {
    updateArticle.mutate({
      id: article.id,
      updates: { is_saved: !article.is_saved }
    });
  };

  const toggleArchived = () => {
    updateArticle.mutate({
      id: article.id,
      updates: { is_archived: !article.is_archived }
    });
  };

  if (!articleId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <p className="text-lg">Select an article to read</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="animate-pulse text-gray-500">Loading article...</div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-red-600">
          <p>Article not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      {/* Toolbar */}
      <div className="border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={toggleSaved}
            className={`px-3 py-1.5 rounded text-sm ${
              article.is_saved
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {article.is_saved ? '★ Saved' : '☆ Save'}
          </button>
          <button
            onClick={toggleArchived}
            className={`px-3 py-1.5 rounded text-sm ${
              article.is_archived
                ? 'bg-gray-100 text-gray-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {article.is_archived ? 'Unarchive' : 'Archive'}
          </button>
        </div>
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
        >
          Open Original →
        </a>
      </div>

      {/* Article Content */}
      <div className="flex-1 overflow-y-auto">
        <article className="max-w-3xl mx-auto p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {article.title}
          </h1>
          {article.author && (
            <p className="text-sm text-gray-600 mb-4">By {article.author}</p>
          )}
          <div className="text-sm text-gray-500 mb-8">
            {new Date(article.published_at || article.fetched_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </div>
          <div
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
        </article>
      </div>
    </div>
  );
}
