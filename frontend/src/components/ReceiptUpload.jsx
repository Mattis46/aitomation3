import React, { useState } from 'react';

export default function ReceiptUpload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      // Demo: Customer mit ID=1
      const res = await fetch(`http://localhost:8000/receipts/upload?customer_id=1`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        throw new Error('Upload fehlgeschlagen');
      }
      const data = await res.json();
      setMessage('Beleg hochgeladen');
      onUploaded && onUploaded(data);
    } catch (err) {
      setMessage(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Beleg hochladen</h2>
      <form onSubmit={handleUpload} className="space-y-2">
        <input
          type="file"
          accept="application/pdf, image/*"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full text-sm"
        />
        <button
          type="submit"
          disabled={uploading || !file}
          className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50"
        >
          {uploading ? 'Lade...' : 'Hochladen'}
        </button>
      </form>
      {message && <p className="text-sm text-gray-600 mt-2">{message}</p>}
    </div>
  );
}