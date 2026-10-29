import { useRef, useState } from 'react';
import { api } from '../services/api';
import Icon from './Icon';

const MAX_IMAGES = 10;
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export default function ImageUpload({ notify }) {
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const addFiles = (incoming) => { const next = [...files]; for (const file of incoming) { if (next.length >= MAX_IMAGES) { notify('You can select up to ' + MAX_IMAGES + ' images.'); break; } if (!IMAGE_TYPES.includes(file.type)) { notify(file.name + ': choose JPEG, PNG, or WebP.'); continue; } if (file.size > MAX_IMAGE_BYTES) { notify(file.name + ': maximum size is 5 MB.'); continue; } if (!next.some((item) => item.name === file.name && item.size === file.size)) next.push(file); } setFiles(next); setMessage(''); };
  const upload = async () => { if (!files.length) return notify('Choose at least one image first.'); setLoading(true); setProgress(0); try { const result = await api.uploadImages(files, setProgress); setMessage(result?.message || 'The backend received the upload.'); } catch (error) { setMessage(error.message || 'Upload failed.'); } finally { setLoading(false); } };
  const clear = () => { if (loading) return; setFiles([]); setMessage(''); setProgress(0); if (inputRef.current) inputRef.current.value = ''; };
  return <div className="image-workspace"><div className="image-disclaimer"><strong>Image processing status</strong><span>This backend validates image files only. No vision model or OCR pipeline is configured.</span></div><button type="button" className={'upload-dropzone ' + (dragging ? 'dragging' : '')} onClick={() => inputRef.current?.click()} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); addFiles(Array.from(event.dataTransfer.files)); }}><span className="upload-icon"><Icon name="upload" size={26} /></span><strong>Drop images here or browse</strong><span>JPEG, PNG, or WebP · up to 10 files · 5 MB each</span></button><input ref={inputRef} className="visually-hidden" type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(event) => { addFiles(Array.from(event.target.files || [])); event.target.value = ''; }} />{files.length > 0 && <div className="image-file-list">{files.map((file, index) => <div className="image-file" key={file.name + '-' + file.size}><img src={URL.createObjectURL(file)} alt="" /><div><strong>{file.name}</strong><span>{(file.size / 1024 / 1024).toFixed(2)} MB</span></div><button type="button" onClick={() => setFiles(files.filter((_, position) => position !== index))} disabled={loading} aria-label={'Remove ' + file.name}>×</button></div>)}</div>}<div className="image-actions"><span>{files.length} / {MAX_IMAGES} selected</span><div><button type="button" className="button quiet" onClick={clear} disabled={!files.length || loading}>Clear</button><button type="button" className="button primary" onClick={upload} disabled={!files.length || loading}>{loading ? 'Uploading ' + progress + '%' : 'Send to backend'}</button></div></div>{message && <div className="notice warning" role="status"><Icon name="warning" size={18} /><div><strong>No image prediction was produced</strong><p>{message}</p></div></div>}</div>;
}
