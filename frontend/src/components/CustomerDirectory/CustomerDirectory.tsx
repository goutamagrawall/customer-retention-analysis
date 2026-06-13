import { useState, useEffect } from 'react';
import axios from 'axios';
import '../../styles/CustomerDirectory.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

interface Customer {
  customer_id: number;
  recency: number;
  frequency: number;
  monetary_total: number;
  churn_score: number;
  rule_segment: string;
  cluster_name: string;
  country: string;
}

export default function CustomerDirectory() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [searchId, setSearchId] = useState('');
  const [selectedSegment, setSelectedSegment] = useState<string>('');
  const [minChurnScore, setMinChurnScore] = useState<number>(0);
  const [loading, setLoading] = useState(false);

  const segments = ['Champions', 'Loyal', 'At_Risk_HighValue', 'Dormant', 'HighEngagement_LowValue', 'Standard'];

  const handleSearch = async () => {
    try {
      setLoading(true);
      if (searchId) {
        const response = await axios.get(`${API_BASE_URL}/customers/${searchId}`);
        setCustomers([response.data]);
      } else {
        const response = await axios.get(`${API_BASE_URL}/customers/search`, {
          params: {
            segment: selectedSegment || undefined,
            min_churn_score: minChurnScore > 0 ? minChurnScore : undefined,
            limit: 50
          }
        });
        setCustomers(response.data);
      }
    } catch (err) {
      console.error('Search failed:', err);
      setCustomers([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="customer-directory">
      <h1>Customer Directory</h1>

      <section className="search-section">
        <div className="search-filters">
          <div className="filter-group">
            <label>Customer ID</label>
            <input
              type="number"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              placeholder="Enter customer ID"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>

          <div className="filter-group">
            <label>Segment</label>
            <select value={selectedSegment} onChange={(e) => setSelectedSegment(e.target.value)}>
              <option value="">All Segments</option>
              {segments.map(seg => (
                <option key={seg} value={seg}>{seg}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Min Churn Score</label>
            <div className="range-container">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={minChurnScore}
                onChange={(e) => setMinChurnScore(parseFloat(e.target.value))}
              />
              <span className="range-value">{(minChurnScore * 100).toFixed(0)}%</span>
            </div>
          </div>

          <button className="search-btn" onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </section>

      <section className="customers-section">
        <h2>Results ({customers.length} customers)</h2>

        {customers.length === 0 && !loading && (
          <p className="no-results">No customers found. Try adjusting your filters.</p>
        )}

        <div className="customers-grid">
          {customers.map(customer => (
            <div key={customer.customer_id} className="customer-card">
              <div className="customer-header">
                <h3>Customer #{customer.customer_id}</h3>
                <span className="churn-badge" style={{
                  backgroundColor: customer.churn_score > 0.7 ? '#e74c3c' : customer.churn_score > 0.4 ? '#f39c12' : '#27ae60'
                }}>
                  {(customer.churn_score * 100).toFixed(0)}% Risk
                </span>
              </div>

              <div className="customer-info">
                <div className="info-row">
                  <span className="label">Segment:</span>
                  <span className="value">{customer.rule_segment}</span>
                </div>
                <div className="info-row">
                  <span className="label">Cluster:</span>
                  <span className="value">{customer.cluster_name}</span>
                </div>
                <div className="info-row">
                  <span className="label">Country:</span>
                  <span className="value">{customer.country || 'Unknown'}</span>
                </div>
              </div>

              <div className="customer-stats">
                <div className="stat">
                  <span className="stat-label">Recency</span>
                  <span className="stat-value">{customer.recency} days</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Frequency</span>
                  <span className="stat-value">{customer.frequency} purchases</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Total Spend</span>
                  <span className="stat-value">${customer.monetary_total.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                </div>
              </div>

              <div className="customer-actions">
                <button className="action-btn">View Profile</button>
                <button className="action-btn secondary">View History</button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
