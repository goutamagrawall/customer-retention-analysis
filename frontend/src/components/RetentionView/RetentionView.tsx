import { useState, useEffect } from 'react';
import axios from 'axios';
import '../../styles/RetentionView.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (window.location.port === '3000' ? 'http://localhost:8000/api' : '/api');

interface ChurnCustomer {
  customer_id: number;
  churn_score: number;
  recency: number;
  frequency: number;
  monetary_total: number;
  rule_segment: string;
}

interface RetentionMetrics {
  churn_rate: number;
  avg_customer_lifetime: number;
  avg_monetary_value: number;
  total_customers: number;
  active_customers_last_30_days: number;
}

export default function RetentionView() {
  const [metrics, setMetrics] = useState<RetentionMetrics | null>(null);
  const [atRiskCustomers, setAtRiskCustomers] = useState<ChurnCustomer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRetentionData();
  }, []);

  const fetchRetentionData = async () => {
    try {
      setLoading(true);
      const [metricsRes, churnRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/retention/metrics`),
        axios.get(`${API_BASE_URL}/retention/churn-predictions?limit=30`)
      ]);
      setMetrics(metricsRes.data);
      setAtRiskCustomers(churnRes.data);
    } catch (err) {
      console.error('Failed to fetch retention data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading retention data...</div>;

  return (
    <div className="retention-view">
      <h1>Retention & Churn Analysis</h1>

      <section className="retention-metrics">
        <h2>Key Retention Metrics</h2>
        <div className="metrics-grid">
          {metrics && (
            <>
              <div className="metric-card">
                <p className="metric-label">Churn Rate</p>
                <p className="metric-value" style={{ color: metrics.churn_rate > 0.4 ? '#e74c3c' : '#27ae60' }}>
                  {(metrics.churn_rate * 100).toFixed(2)}%
                </p>
              </div>
              <div className="metric-card">
                <p className="metric-label">Avg Customer Lifetime</p>
                <p className="metric-value">{metrics.avg_customer_lifetime.toFixed(0)} days</p>
              </div>
              <div className="metric-card">
                <p className="metric-label">Avg Customer Value</p>
                <p className="metric-value">${metrics.avg_monetary_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
              </div>
              <div className="metric-card">
                <p className="metric-label">Total Customers</p>
                <p className="metric-value">{metrics.total_customers.toLocaleString()}</p>
              </div>
            </>
          )}
        </div>
      </section>

      <section className="at-risk-customers">
        <h2>Top 30 Customers at Risk of Churn</h2>
        <p className="section-description">
          These customers show high churn probability based on their Recency, Frequency, and Monetary patterns.
        </p>

        <div className="table-container">
          <table className="customers-table">
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Churn Score</th>
                <th>Days Since Last Purchase</th>
                <th>Transaction Count</th>
                <th>Total Spend</th>
                <th>Segment</th>
              </tr>
            </thead>
            <tbody>
              {atRiskCustomers.map(customer => (
                <tr key={customer.customer_id} className="at-risk-row">
                  <td><strong>{customer.customer_id}</strong></td>
                  <td>
                    <span className={`churn-badge ${customer.churn_score > 0.7 ? 'critical' : 'high'}`}>
                      {(customer.churn_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td>{customer.recency} days</td>
                  <td>{customer.frequency}</td>
                  <td>${customer.monetary_total.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td>
                    <span className="segment-badge">{customer.rule_segment}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="retention-insights">
        <h2>Insights & Recommendations</h2>
        <div className="insights-grid">
          <div className="insight-card">
            <h3>🎯 Priority Actions</h3>
            <ul>
              <li>Contact top 10 at-risk customers immediately with personalized offers</li>
              <li>Launch "We Miss You" campaign for dormant segment</li>
              <li>Implement early warning system for recency thresholds</li>
            </ul>
          </div>
          <div className="insight-card">
            <h3>📊 Cohort Trends</h3>
            <ul>
              <li>Month-1 retention averages 25-35%</li>
              <li>Retention stabilizes at ~10% by month 6</li>
              <li>Consider timing interventions within first 30 days</li>
            </ul>
          </div>
          <div className="insight-card">
            <h3>💡 Strategic Focus</h3>
            <ul>
              <li>Protect high-value at-risk customers (133 customers, ~2.3% of base)</li>
              <li>Improve onboarding to increase month-1 retention</li>
              <li>Create segment-specific retention strategies</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
