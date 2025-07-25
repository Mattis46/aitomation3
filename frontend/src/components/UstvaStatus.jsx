import React from 'react';

export default function UstvaStatus({ ustva }) {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Umsatzsteuervoranmeldung</h2>
      {ustva.length === 0 ? (
        <p className="text-sm text-gray-600">Keine UStVA vorhanden.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="py-1">Zeitraum</th>
              <th className="py-1">Netto</th>
              <th className="py-1">USt</th>
              <th className="py-1">Brutto</th>
            </tr>
          </thead>
          <tbody>
            {ustva.map((u) => (
              <tr key={u.id} className="border-t">
                <td className="py-1">{u.period}</td>
                <td className="py-1">{u.net_sum}</td>
                <td className="py-1">{u.tax_sum}</td>
                <td className="py-1">{u.gross_sum}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}