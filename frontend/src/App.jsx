import React, { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';

/**
 * Haupteinstiegspunkt der React‑Anwendung.
 *
 * Dieses Component entscheidet basierend auf dem Authentifizierungsstatus,
 * ob das Dashboard oder die Login-/Registrierungsseiten angezeigt werden.
 * Nach erfolgreicher Anmeldung oder Registrierung wird der Zustand
 * `authenticated` gesetzt und die App zeigt das Dashboard an.
 */
export default function App() {
  // Authentifizierungsstatus (wird aus LocalStorage initialisiert).
  const [authenticated, setAuthenticated] = useState(false);
  // UI‑Modus: 'login' oder 'register'.
  const [mode, setMode] = useState('login');

  // Beim ersten Render prüfen, ob ein Token existiert.
  useEffect(() => {
    const token = localStorage.getItem('idToken');
    if (token) {
      setAuthenticated(true);
    }
  }, []);

  /**
   * Callback, der nach erfolgreichem Login/Registrierung aufgerufen wird.
   */
  const handleAuthSuccess = () => {
    setAuthenticated(true);
  };

  if (authenticated) {
    return <Dashboard />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center">
      {mode === 'login' ? (
        <>
          <Login onLogin={handleAuthSuccess} />
          <p className="text-center text-sm mt-4">
            Noch keinen Account?{' '}
            <button
              onClick={() => setMode('register')}
              className="text-blue-600 underline"
            >
              Registrieren
            </button>
          </p>
        </>
      ) : (
        <>
          <Register onRegister={handleAuthSuccess} />
          <p className="text-center text-sm mt-4">
            Bereits ein Konto?{' '}
            <button
              onClick={() => setMode('login')}
              className="text-blue-600 underline"
            >
              Anmelden
            </button>
          </p>
        </>
      )}
    </div>
  );
}