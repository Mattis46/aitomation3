import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Firebase configuration for the SaaS project.
// The values are read from Vite environment variables so they can be
// configured per deployment without committing secrets to the codebase.
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: `${import.meta.env.VITE_FIREBASE_PROJECT_ID}.firebaseapp.com`,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: `${import.meta.env.VITE_FIREBASE_PROJECT_ID}.appspot.com`,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase and export the auth instance.
const app = initializeApp(firebaseConfig);

// Firebase Authentication instance used throughout the frontend.
export const auth = getAuth(app);

// Export the app in case it is needed elsewhere.
export default app;