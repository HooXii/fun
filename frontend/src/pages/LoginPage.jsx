import { LockKeyhole, LogIn } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { login } from '../api/client.js';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось войти');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-panel" onSubmit={handleSubmit}>
        <div className="login-title">
          <LockKeyhole size={28} />
          <div>
            <h1>Вход в систему</h1>
            <p>Учет и оптимизация транспортных расходов</p>
          </div>
        </div>
        {error && <div className="alert">{error}</div>}
        <label className="field">
          <span>Email</span>
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label className="field">
          <span>Пароль</span>
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        <button className="primary-button full-width" type="submit" disabled={loading}>
          <LogIn size={18} />
          <span>{loading ? 'Вход...' : 'Войти'}</span>
        </button>
      </form>
    </main>
  );
}

