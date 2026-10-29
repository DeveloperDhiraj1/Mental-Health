import { useState } from 'react';
import { api } from '../services/api';

export default function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = mode === 'login' ? await api.login(email, password) : await api.register(email, password);
      onAuthenticated(user);
    } catch (requestError) {
      setError(requestError.message || 'Unable to complete the request.');
    } finally {
      setLoading(false);
    }
  };
  return <main className="auth-screen"><div className="auth-card"><div className="auth-mark">MS</div><span className="eyebrow">MINDSCOPE AI</span><h1>{mode === 'login' ? 'Sign in' : 'Create an account'}</h1><p>{mode === 'login' ? 'Sign in to use the analysis workspace.' : 'Create a local account for this research workspace.'}</p><form onSubmit={submit}><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /></label>{error && <div className="auth-error" role="alert">{error}</div>}<button className="button primary" disabled={loading}>{loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}</button></form><button className="auth-switch" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}>{mode === 'login' ? 'Need an account? Create one' : 'Already have an account? Sign in'}</button><small>Research tool only. This service does not provide medical diagnosis.</small></div></main>;
}
