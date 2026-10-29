import Icon from './Icon';

const items = [['overview', 'Signal canvas', 'grid'], ['analyze', 'Analysis lab', 'chart'], ['methodology', 'Research notes', 'file'], ['privacy', 'Trust & privacy', 'shield']];

export default function Sidebar({ view, setView, open, setOpen }) {
  return <aside className={'sidebar ' + (open ? 'open' : '')} aria-label="Primary navigation">
    <div className="brand"><span className="brand-mark"><Icon name="shield" size={21} /></span><span><strong>MindScope</strong><small>Signal research studio</small></span></div>
    <div className="workspace-label">WORKSPACE</div>
    <nav className="nav-stack">{items.map(([key, label, icon]) => <button key={key} className={'nav-item ' + (view === key ? 'active' : '')} onClick={() => { setView(key); setOpen(false); }}><Icon name={icon} size={18} /><span>{label}</span>{view === key && <i />}</button>)}</nav>
    <div className="sidebar-spacer" />
    <div className="sidebar-note"><span className="status-dot" /><div><strong>Local research mode</strong><p>Non-clinical text signals</p></div></div>
    <div className="sidebar-footer"><span>MINDSCOPE AI</span><span>v0.1</span></div>
  </aside>;
}
