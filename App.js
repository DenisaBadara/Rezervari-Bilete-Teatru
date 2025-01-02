// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, useLocation } from 'react-router-dom';
import LoginForm from './Components/LoginForm/LoginForm';
import RegisterForm from './Components/RegisterForm/RegisterForm'; // Importă componenta RegisterForm
import Spectacole from './Components/FirstPage/Spectacole';
import './App.css';

function AppWrapper() {
  const location = useLocation();
  let pageClass = '';

  // Aplică clase diferite în funcție de ruta curentă
  if (location.pathname === '/spectacole') {
    pageClass = 'spectacole-page';
  } else if (location.pathname === '/register') {
    pageClass = 'register-page';
  } else {
    pageClass = 'login-page';
  }

  return (
    <div className={pageClass}>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/spectacole" element={<Spectacole />} />
        <Route path="/" element={<Navigate to="/login" />} /> {/* Redirecționează '/' la '/login' */}
        <Route path="*" element={<Navigate to="/login" />} /> {/* Catch-all pentru rute nedefinite */}
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppWrapper />
    </Router>
  );
}

export default App;
