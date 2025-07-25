import React, { useState } from 'react';
import Dashboard from './pages/Dashboard.jsx';
import Login from './pages/Login.jsx';

// Einfacher Zustand, um die Authentifizierung zu simulieren.
export default function App() {
  const [authenticated, setAuthenticated] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {authenticated ? (
        <Dashboard />
      ) : (
        <Login onLogin={() => setAuthenticated(true)} />
      )}
    </div>
  );
}