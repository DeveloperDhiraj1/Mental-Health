import { useEffect, useState } from 'react';
import { api } from './services/api';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Overview from './components/Overview';
import AnalysisWorkspace from './components/AnalysisWorkspace';
import ReadingView from './components/ReadingView';
import AuthScreen from './components/AuthScreen';

export default function App() {
  const [view, setView] = useState('overview');
  const [menuOpen, setMenuOpen] = useState(false);
  const [model, setModel] = useState('checking');
  const [toast, setToast] = useState('');
  const [user, setUser] = useState(null);
  const authRequired = import.meta.env.VITE_AUTH_REQUIRED !== 'false';
  const notify = (message) => { setToast(message); window.setTimeout(() => setToast(''), 3200); };
  useEffect(() => { api.modelInfo().then((data) => setModel(data.available ? 'ready' : 'unavailable')).catch(() => setModel('offline')); }, []);
  useEffect(() => { if (authRequired && api.hasToken()) api.me().then(setUser).catch(() => api.setToken('')); }, [authRequired]);
  if (authRequired && !user) return <AuthScreen onAuthenticated={setUser} />;
  const content = view === 'overview' ? <Overview go={setView} model={model} /> : view === 'analyze' ? <AnalysisWorkspace modelAvailable={model === 'ready'} notify={notify} /> : <ReadingView kind={view} />;
  return <div className="app-shell"><Sidebar view={view} setView={setView} open={menuOpen} setOpen={setMenuOpen} /><main className="main-content"><Topbar view={view} setOpen={setMenuOpen} model={model} toggleTheme={() => document.body.classList.toggle('high-contrast')} onLogout={authRequired ? () => { api.logout(); setUser(null); } : undefined} /><div className="page-wrap">{content}</div></main>{toast && <div className="toast show" role="status" aria-live="polite">{toast}</div>}</div>;
}
