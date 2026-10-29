const MAX_CHARS = 5000;

export default function PostCard({ index, value, onChange, onRemove }) {
  const tooLong = value.length > MAX_CHARS;
  return <article className={'post-card ' + (tooLong ? 'invalid' : '')}><div className="post-head"><span className="post-number">POST {String(index + 1).padStart(2, '0')}</span><button type="button" className="remove-post" onClick={() => onRemove(index)} aria-label={'Remove post ' + (index + 1)}>×</button></div><textarea className="post-input" value={value} onChange={(event) => onChange(index, event.target.value)} maxLength={MAX_CHARS + 1} placeholder="Paste or write a social post to analyze…" aria-label={'Post ' + (index + 1)} /><div className="post-meta"><span className={tooLong ? 'post-error' : ''}>{tooLong ? 'Maximum 5,000 characters' : value.trim() ? 'Ready for review' : 'Waiting for content'}</span><span>{value.length.toLocaleString()} / {MAX_CHARS}</span></div></article>;
}
