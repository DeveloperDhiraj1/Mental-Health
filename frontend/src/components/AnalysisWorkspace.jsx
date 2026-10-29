import { useMemo, useState } from 'react';
import { api } from '../services/api';
import Icon from './Icon';
import PostCard from './PostCard';
import ResultsPanel from './ResultsPanel';
import ImageUpload from './ImageUpload';

const MIN_POSTS = 5;
const MAX_POSTS = 32;
const MAX_CHARS = 5000;

export default function AnalysisWorkspace({ modelAvailable, notify }) {
  const [posts, setPosts] = useState(Array.from({ length: MIN_POSTS }, () => ''));
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const validPosts = useMemo(() => posts.filter((post) => post.trim() && post.trim().length <= MAX_CHARS), [posts]);
  const updatePost = (index, value) => setPosts((current) => current.map((post, position) => position === index ? value : post));
  const removePost = (index) => setPosts((current) => current.filter((_, position) => position !== index));
  const clear = () => { if (posts.some((post) => post.trim()) && !window.confirm('Clear all entered posts?')) return; setPosts(Array.from({ length: MIN_POSTS }, () => '')); setResults(null); };
  const submit = async (event) => { event.preventDefault(); if (validPosts.length < MIN_POSTS) return notify('Add at least five valid posts to continue.'); if (!modelAvailable) return notify('The model is unavailable. No request was sent.'); setLoading(true); setResults(null); try { setResults(await api.batchPredict(validPosts)); } catch (error) { notify(error.message || 'Could not reach the analysis service.'); } finally { setLoading(false); } };
  return <section className="view active analysis-view">
    <div className="analysis-intro"><div><span className="eyebrow">ANALYSIS LAB</span><h1>Review the posts.</h1><p className="lead">Add five or more posts. Nothing is sent until you press Run analysis.</p></div><div className="workspace-badge"><span className="status-dot muted" />{modelAvailable ? 'Model ready' : 'Model unavailable'}</div></div>
    {!modelAvailable && <div className="notice warning"><Icon name="warning" size={18} /><div><strong>Analysis is unavailable</strong><p>The backend has no compatible model configured, so no result will be created.</p></div></div>}
    <form onSubmit={submit} noValidate><div className="lab-panel"><div className="editor-toolbar"><div><span className="eyebrow">01 / TEXT INPUT</span><h2>Add posts to review</h2><p>Up to 32 posts per run · 5,000 characters per post.</p></div><button type="button" className="button secondary" onClick={() => posts.length < MAX_POSTS && setPosts([...posts, ''])} disabled={posts.length >= MAX_POSTS}>＋ Add post</button></div><div className="post-list">{posts.map((post, index) => <PostCard key={index} index={index} value={post} onChange={updatePost} onRemove={removePost} />)}</div><div className="editor-footer"><div className="counter"><span>{validPosts.length}</span> / 5 valid posts<div className="progress-track"><span style={{ width: Math.min(validPosts.length / MIN_POSTS * 100, 100) + '%' }} /></div></div><div className="editor-actions"><button type="button" className="button quiet" onClick={clear}>Clear posts</button><button className="button primary" disabled={loading || validPosts.length < MIN_POSTS}>{loading ? 'Working…' : <>Run analysis <Icon name="arrow" size={16} /></>}</button></div></div></div></form>
    {results && <ResultsPanel items={results} />}
    <div className="analysis-divider"><span>OTHER INPUT</span></div><section className="image-panel"><div className="section-heading"><div><span className="eyebrow">02 / IMAGE FILES</span><h2>Check image uploads</h2></div><span className="subtle-label">Vision model unavailable</span></div><ImageUpload notify={notify} /></section>
  </section>;
}
