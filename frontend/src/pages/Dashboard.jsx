import React, { useEffect, useState } from 'react';
import ReceiptUpload from '../components/ReceiptUpload.jsx';
import ReceiptList from '../components/ReceiptList.jsx';
import UstvaStatus from '../components/UstvaStatus.jsx';
import OpenItems from '../components/OpenItems.jsx';

export default function Dashboard() {
  // Für Demo: lokale Zustände für Daten
  const [receipts, setReceipts] = useState([]);
  const [ustva, setUstva] = useState([]);
  const [openItems, setOpenItems] = useState([]);

  // Daten vom Backend laden (hier nur angedeutet)
  useEffect(() => {
    // In realen Anwendung: fetch("/receipts") etc.
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <ReceiptUpload onUploaded={(rec) => setReceipts([...receipts, rec])} />
          <ReceiptList receipts={receipts} />
        </div>
        <div className="space-y-4">
          <UstvaStatus ustva={ustva} />
          <OpenItems items={openItems} />
        </div>
      </div>
    </div>
  );
}