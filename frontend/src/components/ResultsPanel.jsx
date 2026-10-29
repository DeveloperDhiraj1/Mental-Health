import Icon from './Icon';

export default function ResultsPanel({ items }) {
  return <div className="results-panel"><div className="result-header"><div><span className="eyebrow">BATCH OUTPUT</span><h2>Returned signals</h2></div><span className="subtle-label">{items.length} posts</span></div><div className="notice"><Icon name="shield" size={18} /><div><strong>Research output only</strong><p>These labels describe text content, not a diagnosis or assessment of the author.</p></div></div><div className="result-grid">{items.map((item, index) => <article className="result-card" key={index}><p><strong>Post {String(index + 1).padStart(2, '0')}</strong></p><div>{(item.labels || []).map((label) => <span className="label-chip" key={label}>{label}</span>)}</div></article>)}</div></div>;
}
