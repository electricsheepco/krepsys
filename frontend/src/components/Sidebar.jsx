import { useState } from 'react';
import {
  BookOpen, Inbox, Eye, Bookmark, Archive,
  Rss, Plus, X, Loader2, Trash2
} from 'lucide-react';
import { useFeeds, useCreateFeed, useDeleteFeed } from '../hooks/useFeeds';

const S = {
  bg:       '#1a130d',
  border:   '#2e2218',
  label:    '#6b5040',    /* section labels */
  item:     '#a89278',    /* default nav text */
  itemHov:  '#d4c0a4',
  active:   '#f0e4cc',
  accent:   '#c8762a',
  input:    '#241a12',
  inputBdr: '#3a2a1c',
  footer:   '#4a3828',
};

const filterOptions = [
  { id: 'all',      label: 'All',      icon: Inbox,    filter: {} },
  { id: 'unread',   label: 'Unread',   icon: Eye,      filter: { is_read: false, is_archived: false } },
  { id: 'saved',    label: 'Saved',    icon: Bookmark, filter: { is_saved: true } },
  { id: 'archived', label: 'Archived', icon: Archive,  filter: { is_archived: true } },
];

export default function Sidebar({ selectedFeed, onSelectFeed, filters, onFilterChange }) {
  const { data: feeds, isLoading } = useFeeds();
  const createFeed = useCreateFeed();
  const deleteFeed = useDeleteFeed();
  const [showAdd, setShowAdd] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    let name;
    try { name = new URL(url.trim()).hostname.replace(/^www\./, ''); }
    catch { name = url.trim(); }
    createFeed.mutate({ url: url.trim(), name }, {
      onSuccess: () => { setUrl(''); setShowAdd(false); },
    });
  };

  return (
    <div
      className="w-60 flex flex-col h-screen flex-shrink-0"
      style={{ background: S.bg, borderRight: `1px solid ${S.border}` }}
    >
      {/* Header */}
      <div className="px-4 py-4" style={{ borderBottom: `1px solid ${S.border}` }}>
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: S.accent }}
          >
            <BookOpen size={15} color={S.bg} strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-[14px] font-bold tracking-tight leading-none" style={{ color: S.active }}>
              krep<span>š</span>ys
            </h1>
            <p className="text-[11px] font-medium mt-0.5" style={{ color: S.label }}>
              newsletter reader
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="px-2 pt-5 pb-2">
        <p
          className="px-2 mb-2 text-[10px] font-bold tracking-[0.14em] uppercase"
          style={{ color: S.label }}
        >
          Filters
        </p>
        <div className="space-y-px">
          {filterOptions.map(({ id, label, icon: Icon, filter }) => {
            const isActive = JSON.stringify(filters) === JSON.stringify(filter);
            return (
              <button
                key={id}
                onClick={() => onFilterChange(filter)}
                className={`sidebar-item w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] ${isActive ? 'active' : ''}`}
              >
                <Icon size={14} strokeWidth={isActive ? 2.2 : 1.8} />
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Feeds */}
      <div className="flex-1 overflow-y-auto px-2 pt-5 pb-4">
        <div className="flex items-center justify-between px-2 mb-2">
          <p
            className="text-[10px] font-bold tracking-[0.14em] uppercase"
            style={{ color: S.label }}
          >
            Feeds
          </p>
          <button
            onClick={() => { setShowAdd(v => !v); setUrl(''); }}
            className="w-5 h-5 flex items-center justify-center rounded transition-colors duration-150"
            style={{ color: showAdd ? S.accent : S.label }}
            title={showAdd ? 'Cancel' : 'Add feed'}
          >
            {showAdd ? <X size={14} /> : <Plus size={14} />}
          </button>
        </div>

        {/* Add feed form */}
        <div
          className="overflow-hidden transition-all duration-200 ease-out"
          style={{ maxHeight: showAdd ? '130px' : '0', opacity: showAdd ? 1 : 0 }}
        >
          <form onSubmit={handleSubmit} className="mb-4 px-1 pt-1">
            <input
              type="url"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://example.com/feed"
              className="w-full text-[12px] font-medium rounded-lg px-3 py-2 mb-2 outline-none"
              style={{
                background: S.input,
                color: S.active,
                border: `1px solid ${S.inputBdr}`,
              }}
              autoFocus={showAdd}
            />
            <button
              type="submit"
              disabled={createFeed.isPending}
              className="w-full flex items-center justify-center gap-1.5 text-[12px] font-bold rounded-lg py-2 transition-opacity duration-150 disabled:opacity-60"
              style={{ background: S.accent, color: S.bg }}
            >
              {createFeed.isPending
                ? <><Loader2 size={12} className="animate-spin" /> Adding…</>
                : <><Plus size={12} /> Subscribe</>
              }
            </button>
            {createFeed.isError && (
              <p className="text-[11px] font-medium mt-1.5 px-1" style={{ color: '#e06040' }}>
                {createFeed.error?.response?.data?.detail || 'Failed to add feed'}
              </p>
            )}
          </form>
        </div>

        {/* Feed list */}
        {isLoading ? (
          <div className="space-y-1.5 px-1">
            {[1, 2, 3].map(i => (
              <div key={i} className="shimmer h-8 rounded-lg" />
            ))}
          </div>
        ) : feeds?.length === 0 ? (
          <p className="px-2 text-[12px] font-medium" style={{ color: S.label }}>
            No feeds — add one above
          </p>
        ) : (
          <div className="space-y-px">
            {feeds?.map((feed, i) => {
              const isActive = selectedFeed === feed.id;
              return (
                <div
                  key={feed.id}
                  className={`group flex items-center rounded-lg animate-fade-slide-up ${isActive ? '' : ''}`}
                  style={{ animationDelay: `${i * 0.04}s` }}
                >
                  <button
                    onClick={() => onSelectFeed(feed.id)}
                    className={`sidebar-item flex-1 flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] ${isActive ? 'active' : ''}`}
                  >
                    <Rss
                      size={13}
                      strokeWidth={isActive ? 2.2 : 1.8}
                      style={{ flexShrink: 0, color: isActive ? S.accent : 'inherit' }}
                    />
                    <span className="truncate">{feed.name}</span>
                  </button>
                  {confirmDelete === feed.id ? (
                    <div className="flex items-center gap-1 pr-1">
                      <button
                        onClick={() => { deleteFeed.mutate(feed.id); setConfirmDelete(null); if (selectedFeed === feed.id) onSelectFeed(null); }}
                        className="text-[10px] font-bold px-1.5 py-0.5 rounded transition-colors"
                        style={{ background: '#8b2e10', color: '#fde8d8' }}
                      >yes</button>
                      <button
                        onClick={() => setConfirmDelete(null)}
                        className="text-[10px] font-bold px-1.5 py-0.5 rounded"
                        style={{ color: S.label }}
                      >no</button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirmDelete(feed.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity pr-2"
                      style={{ color: S.label }}
                      title="Delete feed"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3" style={{ borderTop: `1px solid ${S.border}` }}>
        <p className="text-[11px] font-medium" style={{ color: S.footer }}>
          krepšys · self-hosted
        </p>
      </div>
    </div>
  );
}
