// src/Components/Spectacole/Spectacole.jsx
import React, { useState, useEffect } from 'react';
import './Spectacole.css';

const SpectacolePage = () => {
  const [spectacole, setSpectacole] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/spectacole')
      .then(response => {
        if (!response.ok) {
          throw new Error('Nu s-au putut încărca spectacolele');
        }
        return response.json();
      })
      .then(data => setSpectacole(data))
      .catch(err => setError(err.message));
  }, []);

  return (
    <div className="spectacole-container">
      <h2>Spectacole Disponibile</h2>
      {error && <p className="error">{error}</p>}
      <table className="spectacole-table">
        <thead>
          <tr>
            <th>Nume Spectacol</th>
            <th>Tip Spectacol</th>
            <th>Nume Sala</th>
            <th>Capacitate</th>
            <th>Tip Sala</th>
            <th>Ziua Spectacolului</th>
            <th>Data</th>
            <th>Ora</th>
          </tr>
        </thead>
        <tbody>
          {spectacole.map(spectacol => (
            <tr key={spectacol.SpectacolID}>
              <td>{spectacol.Nume_spectacol}</td>
              <td>{spectacol.Tip_spectacol}</td>
              <td>{spectacol.Nume_sala}</td>
              <td>{spectacol.Capacitate}</td>
              <td>{spectacol.Tip_sala}</td>
              <td>{spectacol.Ziua_spectacolului}</td>
              <td>{spectacol.Data}</td>
              <td>{spectacol.Ora}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SpectacolePage;
