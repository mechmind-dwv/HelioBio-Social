// frontend/src/App.tsx
import React from 'react';
import './styles/globals.css';
import { Dashboard } from './pages/Dashboard';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Footer } from './components/layout/Footer';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />
      <div className="main-content">
        <Sidebar />
        <main className="page-content">
          <Dashboard />
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default App;
