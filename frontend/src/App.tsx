import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Dashboard from './pages/Dashboard';
import SegmentationView from './components/SegmentationView/SegmentationView';
import RetentionView from './components/RetentionView/RetentionView';
import CustomerDirectory from './components/CustomerDirectory/CustomerDirectory';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/metrics`);
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !metrics) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error && !metrics) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Customer Retention & Segmentation Platform</h1>
        <p>Industry-grade analytics for customer insights</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`nav-btn ${activeTab === 'segmentation' ? 'active' : ''}`}
          onClick={() => setActiveTab('segmentation')}
        >
          🎯 Segmentation
        </button>
        <button
          className={`nav-btn ${activeTab === 'retention' ? 'active' : ''}`}
          onClick={() => setActiveTab('retention')}
        >
          📈 Retention & Churn
        </button>
        <button
          className={`nav-btn ${activeTab === 'customers' ? 'active' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          👥 Customer Directory
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'overview' && <Dashboard metrics={metrics} />}
        {activeTab === 'segmentation' && <SegmentationView />}
        {activeTab === 'retention' && <RetentionView />}
        {activeTab === 'customers' && <CustomerDirectory />}
      </main>

      <footer className="app-footer">
        <p>© 2024 Customer Retention Analytics. Data as of Dec 2011.</p>
      </footer>
    </div>
  );
}

export default App;
