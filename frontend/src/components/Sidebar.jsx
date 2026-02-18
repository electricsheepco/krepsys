import { useFeeds } from '../hooks/useFeeds';

export default function Sidebar({ selectedFeed, onSelectFeed, filters, onFilterChange }) {
  const { data: feeds, isLoading } = useFeeds();

  const filterOptions = [
    { id: 'all', label: 'All Articles', filter: {} },
    { id: 'unread', label: 'Unread', filter: { is_read: false, is_archived: false } },
    { id: 'saved', label: 'Saved', filter: { is_saved: true } },
    { id: 'archived', label: 'Archived', filter: { is_archived: true } },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-800">Krepsys</h1>
        <p className="text-xs text-gray-500 mt-1">Newsletter Reader</p>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xs font-semibold text-gray-500 uppercase mb-2">Filters</h2>
        <div className="space-y-1">
          {filterOptions.map(option => (
            <button
              key={option.id}
              onClick={() => onFilterChange(option.filter)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${
                JSON.stringify(filters) === JSON.stringify(option.filter)
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Feeds */}
      <div className="flex-1 overflow-y-auto p-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase mb-2">Feeds</h2>
        {isLoading ? (
          <p className="text-sm text-gray-500">Loading feeds...</p>
        ) : feeds?.length === 0 ? (
          <p className="text-sm text-gray-500">No feeds yet</p>
        ) : (
          <div className="space-y-1">
            {feeds?.map(feed => (
              <button
                key={feed.id}
                onClick={() => onSelectFeed(feed.id)}
                className={`w-full text-left px-3 py-2 rounded text-sm ${
                  selectedFeed === feed.id
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                {feed.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
