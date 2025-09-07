// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

// Конфигурация API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://hr-avatar-backend.onrender.com';

function App() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка списка кандидатов
  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/`);
      if (!response.ok) {
        throw new Error('Failed to fetch candidates');
      }
      const data = await response.json();
      setCandidates(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to upload file');
      }
      
      const result = await response.json();
      console.log('Upload successful:', result);
      
      // Обновляем список кандидатов
      fetchCandidates();
    } catch (err) {
      setError(err.message);
    }
  };

  const generateInterviewExample = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/generate-example`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate example');
      }
      
      const result = await response.json();
      console.log('Example generated:', result);
      alert('Пример интервью успешно создан!');
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>Ошибка: {error}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>HR Avatar System</h1>
        <p>Система автоматизации HR-процессов</p>
      </header>

      <main className="App-main">
        <section className="upload-section">
          <h2>Загрузка резюме</h2>
          <input 
            type="file" 
            accept=".pdf,.doc,.docx" 
            onChange={handleFileUpload}
            className="file-input"
          />
        </section>

        <section className="actions-section">
          <button onClick={generateInterviewExample} className="action-button">
            Создать пример интервью
          </button>
        </section>

        <section className="candidates-section">
          <h2>Кандидаты ({candidates.length})</h2>
          {candidates.length === 0 ? (
            <p>Пока нет кандидатов</p>
          ) : (
            <div className="candidates-list">
              {candidates.map(candidate => (
                <div key={candidate.id} className="candidate-card">
                  <h3>{candidate.name}</h3>
                  <p><strong>Должность:</strong> {candidate.position}</p>
                  <p><strong>Email:</strong> {candidate.email}</p>
                  <p><strong>Статус:</strong> {candidate.status}</p>
                  <p><strong>Соответствие:</strong> {candidate.match_percentage}%</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="App-footer">
        <p>HR Avatar System &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;