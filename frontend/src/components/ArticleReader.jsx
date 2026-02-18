import { useEffect, useState, useRef, useCallback } from 'react';
import {
  Bookmark, BookmarkCheck, Archive, ArchiveRestore, ExternalLink,
  Tag, StickyNote, Highlighter, X, Plus, Trash2
} from 'lucide-react';
import { useArticle, useUpdateArticle } from '../hooks/useArticles';
import { useArticleTags, useAllTags } from '../hooks/useFeeds';
import { useHighlights, useCreateHighlight, useDeleteHighlight } from '../hooks/useHighlights';

const C = {
  bg:       '#faf5ec',
  border:   '#ddd4c0',
  toolbar:  '#f5efe4',
  title:    '#1e1408',
  meta:     '#7a6850',
  body:     '#2c2018',
  btnBg:    '#ece4d4',
  btnColor: '#5a4832',
  btnHov:   '#e0d8c4',
  accent:   '#c8762a',
  accentBg: '#faebd4',
  panelBg:  '#f0e8d8',
};

const HIGHLIGHT_COLORS = {
  yellow: '#fef08a',
  green:  '#bbf7d0',
  blue:   '#bfdbfe',
  pink:   '#fbcfe8',
};

// ── Apply highlights to HTML string ──────────────────────────────────────────
function applyHighlights(html, highlights) {
  if (!highlights?.length || !html) return html;
  let result = html;
  highlights.forEach(h => {
    const escaped = h.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`(${escaped})`, 'g');
    result = result.replace(
      re,
      `<mark style="background:${HIGHLIGHT_COLORS[h.color] || HIGHLIGHT_COLORS.yellow};border-radius:2px;padding:0 1px" data-hid="${h.id}">$1</mark>`
    );
  });
  return result;
}

export default function ArticleReader({ articleId }) {
  const { data: article, isLoading } = useArticle(articleId);
  const updateArticle  = useUpdateArticle();
  const { add: addTag, remove: removeTag } = useArticleTags(articleId);
  const { data: allTags = [] } = useAllTags();
  const { data: highlights = [] } = useHighlights(articleId);
  const createHighlight = useCreateHighlight(articleId);
  const deleteHighlight = useDeleteHighlight(articleId);

  const [activePanel, setActivePanel] = useState(null); // 'notes' | 'tags' | 'highlights'
  const [noteText, setNoteText]       = useState('');
  const [noteDirty, setNoteDirty]     = useState(false);
  const [tagInput, setTagInput]       = useState('');
  const [highlightPopup, setHighlightPopup] = useState(null); // { x, y, text }
  const contentRef = useRef(null);

  useEffect(() => {
    if (article && !article.is_read)
      updateArticle.mutate({ id: article.id, updates: { is_read: true } });
  }, [article?.id]);

  useEffect(() => {
    if (article) { setNoteText(article.note || ''); setNoteDirty(false); }
  }, [article?.id]);

  const saveNote = useCallback(() => {
    if (!noteDirty) return;
    updateArticle.mutate({ id: article.id, updates: { note: noteText } });
    setNoteDirty(false);
  }, [article?.id, noteText, noteDirty]);

  // Text selection → highlight popup
  const handleMouseUp = useCallback(() => {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.toString().trim()) {
      setHighlightPopup(null);
      return;
    }
    const range = sel.getRangeAt(0);
    const rect  = range.getBoundingClientRect();
    const containerRect = contentRef.current?.getBoundingClientRect();
    if (!containerRect) return;
    setHighlightPopup({
      x: rect.left - containerRect.left + rect.width / 2,
      y: rect.top  - containerRect.top - 44,
      text: sel.toString().trim(),
    });
  }, []);

  const saveHighlight = (color) => {
    if (!highlightPopup?.text) return;
    createHighlight.mutate({ text: highlightPopup.text, color });
    window.getSelection()?.removeAllRanges();
    setHighlightPopup(null);
  };

  const toggleSaved    = () => updateArticle.mutate({ id: article.id, updates: { is_saved:    !article.is_saved } });
  const toggleArchived = () => updateArticle.mutate({ id: article.id, updates: { is_archived: !article.is_archived } });

  const togglePanel = (name) => setActivePanel(p => p === name ? null : name);

  // ── Empty state ─────────────────────────────────────────────────────────────
  if (!articleId) {
    return (
      <div className="flex-1 flex items-center justify-center" style={{ background: C.bg }}>
        <div className="text-center">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: C.btnBg }}>
            <BookmarkCheck size={20} style={{ color: C.meta }} strokeWidth={1.5} />
          </div>
          <p className="text-[13px] font-semibold" style={{ color: C.meta }}>Select an article</p>
          <p className="text-[12px] mt-1 font-medium" style={{ color: '#b0a080' }}>Pick something from the list</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col h-screen" style={{ background: C.bg }}>
        <div className="px-8 py-4 flex gap-2" style={{ borderBottom: `1px solid ${C.border}`, background: C.toolbar }}>
          <div className="shimmer h-8 rounded-lg w-20" /><div className="shimmer h-8 rounded-lg w-20" />
        </div>
        <div className="flex-1 p-10 max-w-2xl mx-auto w-full space-y-4">
          <div className="shimmer h-7 rounded-lg w-4/5" />
          <div className="shimmer h-4 rounded-lg w-1/3" />
          <div className="mt-8 space-y-3">
            {[100,95,88,100,92,78,96].map((w,i) => (
              <div key={i} className="shimmer h-4 rounded-lg" style={{ width: `${w}%` }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="flex-1 flex items-center justify-center" style={{ background: C.bg }}>
        <p className="text-[13px] font-semibold" style={{ color: '#c04030' }}>Article not found</p>
      </div>
    );
  }

  const renderedContent = applyHighlights(article.content, highlights);

  return (
    <div className="flex-1 flex flex-col h-screen" style={{ background: C.bg }}>

      {/* ── Toolbar ──────────────────────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-5 py-2.5 flex-shrink-0"
        style={{ borderBottom: `1px solid ${C.border}`, background: C.toolbar }}
      >
        <div className="flex items-center gap-1.5">
          <Btn onClick={toggleSaved} active={article.is_saved} activeBg={C.accentBg} activeColor={C.accent}>
            {article.is_saved ? <BookmarkCheck size={14} strokeWidth={2.2} /> : <Bookmark size={14} strokeWidth={2} />}
            <span>{article.is_saved ? 'Saved' : 'Save'}</span>
          </Btn>
          <Btn onClick={toggleArchived} active={article.is_archived}>
            {article.is_archived ? <ArchiveRestore size={14} strokeWidth={2} /> : <Archive size={14} strokeWidth={2} />}
            <span>{article.is_archived ? 'Unarchive' : 'Archive'}</span>
          </Btn>

          <div className="w-px h-5 mx-1" style={{ background: C.border }} />

          {/* Annotation toggles */}
          <PanelBtn icon={StickyNote}  label="Note"       active={activePanel === 'notes'}      onClick={() => togglePanel('notes')}      dot={!!article.note} />
          <PanelBtn icon={Tag}         label="Tags"       active={activePanel === 'tags'}       onClick={() => togglePanel('tags')}       dot={article.tags?.length > 0} />
          <PanelBtn icon={Highlighter} label="Highlights" active={activePanel === 'highlights'} onClick={() => togglePanel('highlights')} dot={highlights.length > 0} />
        </div>

        <a
          href={article.url} target="_blank" rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-[12px] font-semibold px-3 py-1.5 rounded-lg transition-colors duration-150"
          style={{ color: C.btnColor, background: C.btnBg }}
          onMouseEnter={e => e.currentTarget.style.background = C.btnHov}
          onMouseLeave={e => e.currentTarget.style.background = C.btnBg}
        >
          Original <ExternalLink size={12} strokeWidth={2.2} />
        </a>
      </div>

      {/* ── Annotation panel ─────────────────────────────────────────────────── */}
      {activePanel && (
        <div
          className="flex-shrink-0 px-6 py-4 animate-fade-in"
          style={{ background: C.panelBg, borderBottom: `1px solid ${C.border}` }}
        >
          {activePanel === 'notes' && (
            <NotePanel
              value={noteText}
              onChange={v => { setNoteText(v); setNoteDirty(true); }}
              onBlur={saveNote}
              saving={updateArticle.isPending}
            />
          )}
          {activePanel === 'tags' && (
            <TagsPanel
              article={article}
              allTags={allTags}
              tagInput={tagInput}
              setTagInput={setTagInput}
              addTag={addTag}
              removeTag={removeTag}
            />
          )}
          {activePanel === 'highlights' && (
            <HighlightsPanel highlights={highlights} deleteHighlight={deleteHighlight} />
          )}
        </div>
      )}

      {/* ── Article content ───────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto" ref={contentRef} style={{ position: 'relative' }}>

        {/* Highlight selection popup */}
        {highlightPopup && (
          <div
            className="absolute z-50 flex items-center gap-1 px-2 py-1.5 rounded-xl shadow-lg animate-fade-in"
            style={{
              left: highlightPopup.x - 80,
              top: highlightPopup.y,
              background: '#2c1f14',
              border: '1px solid #4a3828',
            }}
          >
            <span className="text-[10px] font-semibold mr-1" style={{ color: '#a89278' }}>Highlight</span>
            {Object.entries(HIGHLIGHT_COLORS).map(([name, hex]) => (
              <button
                key={name}
                onClick={() => saveHighlight(name)}
                className="w-5 h-5 rounded-full border-2 transition-transform duration-100 hover:scale-125"
                style={{ background: hex, borderColor: '#4a3828' }}
                title={name}
              />
            ))}
            <button onClick={() => setHighlightPopup(null)} className="ml-1" style={{ color: '#6b5040' }}>
              <X size={12} />
            </button>
          </div>
        )}

        <article key={article.id} className="max-w-2xl mx-auto px-10 py-10 animate-fade-in" onMouseUp={handleMouseUp}>
          <h1 className="text-2xl font-bold leading-tight mb-3" style={{ color: C.title }}>
            {article.title}
          </h1>
          <div className="flex items-center gap-2 mb-8">
            {article.author && <span className="text-[13px] font-semibold" style={{ color: C.meta }}>{article.author}</span>}
            {article.author && <span style={{ color: C.border }}>·</span>}
            <span className="text-[13px] font-medium" style={{ color: C.meta }}>
              {new Date(article.published_at || article.fetched_at).toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric'
              })}
            </span>
            {article.tags?.length > 0 && (
              <div className="flex items-center gap-1 ml-2">
                {article.tags.map(t => (
                  <span key={t.id} className="text-[10px] font-semibold px-1.5 py-0.5 rounded-md" style={{ background: C.accentBg, color: C.accent }}>
                    {t.name}
                  </span>
                ))}
              </div>
            )}
          </div>

          {article.content ? (
            <div
              className="prose prose-base max-w-none"
              style={{
                '--tw-prose-body':          C.body,
                '--tw-prose-headings':      C.title,
                '--tw-prose-links':         C.accent,
                '--tw-prose-bold':          C.title,
                '--tw-prose-hr':            C.border,
                '--tw-prose-quotes':        C.meta,
                '--tw-prose-quote-borders': C.accent,
                lineHeight: '1.8',
                fontSize: '15px',
              }}
              dangerouslySetInnerHTML={{ __html: renderedContent }}
            />
          ) : (
            <p className="text-[14px] font-medium" style={{ color: C.meta }}>No content available.</p>
          )}
        </article>
      </div>
    </div>
  );
}

// ── Sub-components ───────────────────────────────────────────────────────────

function Btn({ onClick, active, activeBg, activeColor, children }) {
  const bg    = active ? (activeBg    || '#e4dbd0') : '#ece4d4';
  const color = active ? (activeColor || '#2c2018') : '#5a4832';
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 text-[12px] font-semibold px-3 py-1.5 rounded-lg transition-colors duration-150"
      style={{ background: bg, color }}
      onMouseEnter={e => e.currentTarget.style.background = active ? bg : '#e0d8c4'}
      onMouseLeave={e => e.currentTarget.style.background = bg}
    >
      {children}
    </button>
  );
}

function PanelBtn({ icon: Icon, label, active, onClick, dot }) {
  return (
    <button
      onClick={onClick}
      className="relative flex items-center gap-1.5 text-[12px] font-semibold px-2.5 py-1.5 rounded-lg transition-colors duration-150"
      style={{ background: active ? '#e4dbd0' : 'transparent', color: active ? '#c8762a' : '#7a6850' }}
      onMouseEnter={e => { if (!active) e.currentTarget.style.background = '#ece4d4'; }}
      onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}
      title={label}
    >
      <Icon size={14} strokeWidth={active ? 2.2 : 1.8} />
      <span className="hidden sm:inline">{label}</span>
      {dot && (
        <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full" style={{ background: '#c8762a' }} />
      )}
    </button>
  );
}

function NotePanel({ value, onChange, onBlur, saving }) {
  return (
    <div>
      <p className="text-[11px] font-bold uppercase tracking-widest mb-2" style={{ color: '#7a6850' }}>Personal Note</p>
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        onBlur={onBlur}
        rows={4}
        placeholder="Add a note to this article…"
        className="w-full text-[13px] font-medium rounded-xl px-4 py-3 outline-none resize-none transition-colors duration-150"
        style={{ background: '#ece4d4', color: '#2c2018', border: '1px solid #ddd4c0', lineHeight: '1.6' }}
      />
      {saving && <p className="text-[11px] mt-1" style={{ color: '#a89278' }}>Saving…</p>}
    </div>
  );
}

function TagsPanel({ article, allTags, tagInput, setTagInput, addTag, removeTag }) {
  const suggestions = allTags.filter(t =>
    tagInput.length > 0 &&
    t.name.includes(tagInput.toLowerCase()) &&
    !article.tags?.find(at => at.id === t.id)
  );

  const submit = (name) => {
    const n = (name || tagInput).trim().toLowerCase();
    if (!n) return;
    addTag.mutate(n);
    setTagInput('');
  };

  return (
    <div>
      <p className="text-[11px] font-bold uppercase tracking-widest mb-2" style={{ color: '#7a6850' }}>Tags</p>
      <div className="flex flex-wrap gap-1.5 mb-3">
        {article.tags?.map(t => (
          <span
            key={t.id}
            className="flex items-center gap-1 text-[12px] font-semibold px-2.5 py-1 rounded-lg"
            style={{ background: '#faebd4', color: '#c8762a' }}
          >
            {t.name}
            <button onClick={() => removeTag.mutate(t.name)} className="hover:opacity-70 transition-opacity">
              <X size={11} />
            </button>
          </span>
        ))}
        {(!article.tags || article.tags.length === 0) && (
          <span className="text-[12px] font-medium" style={{ color: '#a89278' }}>No tags yet</span>
        )}
      </div>
      <div className="relative flex items-center gap-2">
        <input
          value={tagInput}
          onChange={e => setTagInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
          placeholder="Add tag…"
          className="flex-1 text-[12px] font-medium rounded-lg px-3 py-1.5 outline-none"
          style={{ background: '#ece4d4', color: '#2c2018', border: '1px solid #ddd4c0' }}
        />
        <button
          onClick={() => submit()}
          className="flex items-center gap-1 text-[12px] font-bold px-2.5 py-1.5 rounded-lg transition-colors duration-150"
          style={{ background: '#c8762a', color: '#faf5ec' }}
        >
          <Plus size={12} /> Add
        </button>
        {suggestions.length > 0 && (
          <div
            className="absolute top-full left-0 mt-1 z-10 rounded-xl overflow-hidden shadow-lg"
            style={{ background: '#ece4d4', border: '1px solid #ddd4c0', minWidth: '140px' }}
          >
            {suggestions.map(t => (
              <button
                key={t.id}
                onClick={() => submit(t.name)}
                className="w-full text-left px-3 py-1.5 text-[12px] font-medium transition-colors duration-100"
                style={{ color: '#2c2018' }}
                onMouseEnter={e => e.currentTarget.style.background = '#e0d8c4'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                {t.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function HighlightsPanel({ highlights, deleteHighlight }) {
  if (!highlights.length) {
    return (
      <div>
        <p className="text-[11px] font-bold uppercase tracking-widest mb-2" style={{ color: '#7a6850' }}>Highlights</p>
        <p className="text-[12px] font-medium" style={{ color: '#a89278' }}>
          Select text in the article to highlight it
        </p>
      </div>
    );
  }
  return (
    <div>
      <p className="text-[11px] font-bold uppercase tracking-widest mb-2" style={{ color: '#7a6850' }}>
        Highlights ({highlights.length})
      </p>
      <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
        {highlights.map(h => (
          <div
            key={h.id}
            className="flex items-start gap-2 px-3 py-2 rounded-xl"
            style={{ background: HIGHLIGHT_COLORS[h.color] + 'cc' }}
          >
            <p className="flex-1 text-[12px] font-medium leading-snug" style={{ color: '#2c2018' }}>
              "{h.text}"
            </p>
            <button
              onClick={() => deleteHighlight.mutate(h.id)}
              className="flex-shrink-0 transition-opacity hover:opacity-70 mt-0.5"
              style={{ color: '#7a6850' }}
            >
              <Trash2 size={12} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
