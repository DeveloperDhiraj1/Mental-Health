import Icon from './Icon';

function Stat({ icon, tone, label, value, note }) {
  return <article className="stat-card"><div className={'stat-icon ' + tone}><Icon name={icon} size={17} /></div><span className="stat-label">{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

export default function Overview({ go, model }) {
  return <section className="view active">
    <div className="welcome-row"><div><span className="eyebrow">MINDSCOPE AI</span><h1>Review posts.<br /><em>Keep context.</em></h1><p className="hero-copy">Paste social posts, send them for analysis, and review the returned text labels. This is a research tool, not a medical assessment.</p><div className="hero-actions"><button className="button primary" onClick={() => go('analyze')}>Review posts <Icon name="arrow" size={17} /></button><button className="button quiet" onClick={() => go('methodology')}>Read the notes</button></div></div><div className="hero-visual"><div className="hero-orbit orbit-a" /><div className="hero-orbit orbit-b" /><div className="signal-card"><div className="signal-card-top"><span className="mini-dot" />LOCAL WORKSPACE</div><div className="signal-bars">{[42, 70, 48, 86, 62, 94, 54, 76, 39, 66].map((height, i) => <i key={i} style={{ height: height + '%' }} />)}</div><div className="signal-card-bottom"><span>Current view</span><strong>Text review</strong></div></div><span className="visual-caption">TEXT / CONTEXT / CARE</span></div></div>
    <div className="section-heading"><div><span className="eyebrow">PROJECT DETAILS</span><h2>What is available</h2></div><span className="freshness">Local project data</span></div>
    <div className="stat-grid"><Stat icon="chart" tone="sage" label="Source records" value="4,739" note="YouTube · Reddit · X" /><Stat icon="shield" tone="mint" label="Reviewed sample" value="60" note="20 from each platform" /><Stat icon="sun" tone="sand" label="Service status" value={model === 'ready' ? 'Ready' : 'Offline'} note={model === 'ready' ? 'Model loaded' : 'Model not configured'} /><Stat icon="shield" tone="rose" label="Use of results" value="Text only" note="No diagnosis or risk score" /></div>
    <div className="overview-foot"><span className="status-dot muted" /><span>Labels describe words in a post. They do not describe its author.</span></div>
  </section>;
}
