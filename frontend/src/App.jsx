import { useState } from 'react';
import Sidebar from './components/Sidebar';
import ArticleList from './components/ArticleList';
import ArticleReader from './components/ArticleReader';

function App() {
  const [filters, setFilters] = useState({});
  const [selectedFeed, setSelectedFeed] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);

  const handleSelectFeed = (feedId) => {
    setSelectedFeed(feedId);
    setFilters({ ...filters, feed_id: feedId });
    setSelectedArticle(null);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setSelectedFeed(null);
    setSelectedArticle(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        selectedFeed={selectedFeed}
        onSelectFeed={handleSelectFeed}
        filters={filters}
        onFilterChange={handleFilterChange}
      />
      <ArticleList
        filters={filters}
        selectedArticle={selectedArticle}
        onSelectArticle={setSelectedArticle}
      />
      <ArticleReader articleId={selectedArticle} />
    </div>
  );
}

export default App;
