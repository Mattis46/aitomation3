import React from 'react';

export default function ReceiptList({ receipts }) {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Hochgeladene Belege</h2>
      {receipts.length === 0 ? (
        <p className="text-sm text-gray-600">Keine Belege vorhanden.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="py-1">Datum</th>
              <th className="py-1">Lieferant</th>
              <th className="py-1">Netto</th>
              <th className="py-1">USt</th>
              <th className="py-1">Brutto</th>
            </tr>
          </thead>
          <tbody>
            {receipts.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="py-1">{r.date || '-'}</td>
                <td className="py-1">{r.supplier || '-'}</td>
                <td className="py-1">{r.net_amount ?? '-'}</td>
                <td className="py-1">{r.tax_amount ?? '-'}</td>
                <td className="py-1">{r.gross_amount ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}