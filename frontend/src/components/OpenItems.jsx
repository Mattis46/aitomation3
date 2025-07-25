import React from 'react';

export default function OpenItems({ items }) {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Offene Posten</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-600">Keine offenen Posten.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="py-1">Beschreibung</th>
              <th className="py-1">Betrag</th>
              <th className="py-1">Fällig am</th>
              <th className="py-1">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-t">
                <td className="py-1">{item.description}</td>
                <td className="py-1">{item.amount}</td>
                <td className="py-1">{item.due_date}</td>
                <td className="py-1">{item.paid ? 'bezahlt' : 'offen'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}