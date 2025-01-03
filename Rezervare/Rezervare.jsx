// src/Components/Rezervare/Rezervare.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Rezervare.css';

const Rezervare = () => {
  const { spectacolId } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    cantitate_bilete: '',
    nume: '',
    prenume: '',
    email: '',
    numar_telefon: ''
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Fetch user details to prefill the form
  useEffect(() => {
    fetch('http://localhost:5000/user-details', { credentials: 'include' })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Nu s-au putut încărca detaliile utilizatorului.');
      })
      .then((data) => {
        setFormData((prevData) => ({
          ...prevData,
          nume: data.nume || '',
          prenume: data.prenume || '',
          email: data.email || '',
          numar_telefon: data.numar_telefon || ''
        }));
      })
      .catch((err) => {
        console.error('Eroare la obținerea detaliilor utilizatorului:', err);
        setError('Nu s-au putut încărca detaliile utilizatorului.');
      });
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Validare simplă
    if (
      !formData.cantitate_bilete ||
      !formData.nume ||
      !formData.prenume ||
      !formData.email ||
      !formData.numar_telefon
    ) {
      setError('Te rog să completezi toate câmpurile.');
      setSuccess(null);
      return;
    }

    // Trimitere date către backend
    fetch('http://localhost:5000/rezervare', {
      method: 'POST',
      credentials: 'include', // Pentru a trimite cookie-urile de sesiune
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        spectacolId,
        ...formData
      })
    })
      .then((response) => {
        if (response.ok) {
          setSuccess('Rezervare realizată cu succes!');
          setError(null);
          // Redirecționează după un timp
          setTimeout(() => {
            navigate('/spectacole');
          }, 2000);
        } else {
          return response.json().then((data) => {
            throw new Error(data.message || 'Eroare la rezervare.');
          });
        }
      })
      .catch((err) => {
        setError(err.message);
        setSuccess(null);
      });
  };

  return (
    <div className="rezervare-container">
      <h2>Rezervare Bilete</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Cantitate Bilete:</label>
          <input
            type="number"
            name="cantitate_bilete"
            value={formData.cantitate_bilete}
            onChange={handleChange}
            min="1"
            required
          />
        </div>
        <div className="form-group">
          <label>Nume:</label>
          <input
            type="text"
            name="nume"
            value={formData.nume}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Prenume:</label>
          <input
            type="text"
            name="prenume"
            value={formData.prenume}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Număr Telefon:</label>
          <input
            type="tel"
            name="numar_telefon"
            value={formData.numar_telefon}
            onChange={handleChange}
            required
          />
        </div>
        <div className="buttons-container">
          <button type="submit">Rezervă</button>
          <button type="button" onClick={() => navigate('/spectacole')}>
            Înapoi
          </button>
        </div>
      </form>
    </div>
  );
};

export default Rezervare;
