import React, { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase.js';

/**
 * Login‑Seite für bestehende Nutzer.
 *
 * Bei erfolgreichem Login wird das Firebase ID‑Token in den LocalStorage
 * geschrieben und der Callback `onLogin` aufgerufen, um den
 * Authentifizierungsstatus im Eltern‑Component zu aktualisieren.
 */
export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  /**
   * Meldet den Benutzer mittels Firebase E‑Mail/Passwort‑Authentifizierung an.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { user } = await signInWithEmailAndPassword(auth, email, password);
      // Nach dem Login das ID‑Token holen und speichern.
      const idToken = await user.getIdToken();
      localStorage.setItem('idToken', idToken);
      // Callback ausführen, damit App den Status aktualisiert.
      if (onLogin) onLogin();
    } catch (err) {
      // Fehler (z. B. falsches Passwort) anzeigen.
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Anmeldung</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-2 text-sm text-red-700 bg-red-100 rounded">{error}</div>
        )}
        <div>
          <label htmlFor="email" className="block text-sm font-medium">
            E‑Mail
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium">
            Passwort
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Anmelden…' : 'Anmelden'}
        </button>
      </form>
    </div>
  );
}