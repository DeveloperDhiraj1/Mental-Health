import Icon from './Icon';

export default function Topbar({ view, setOpen, model, toggleTheme, onLogout }) {
  const names = { overview: 'Signal canvas', analyze: 'Analysis lab', methodology: 'Research notes', privacy: 'Trust & privacy' };
  return <header className="topbar"><button className="mobile-menu" onClick={() => setOpen(true)} aria-label="Open navigation"><span /><span /><span /></button><div className="breadcrumb"><span>Workspace</span><b>/</b><strong>{names[view]}</strong></div><div className="topbar-actions"><span className="api-status"><span className={'status-dot ' + (model === 'ready' ? '' : 'muted')} />{model === 'ready' ? 'Model connected' : model === 'offline' ? 'Backend offline' : 'Model unavailable'}</span><button className="icon-button" onClick={toggleTheme} aria-label="Toggle contrast theme"><Icon name="sun" size={18} /></button>{onLogout && <button className="logout-button" onClick={onLogout}>Sign out</button>}<span className="avatar">MS</span></div></header>;
}
