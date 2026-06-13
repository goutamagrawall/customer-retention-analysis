import { useMemo } from 'react';
import '../styles/Dashboard.css';

interface MetricsData {
  total_customers: number;
  active_customers: number;
  churned_customers: number;
  churn_rate: number;
  total_revenue: number;
  avg_customer_ltv: number;
  segments: Array<{ segment: string; count: number; percentage: number }>;
}

interface DashboardProps {
  metrics: MetricsData;
}

export default function Dashboard({ metrics }: DashboardProps) {
  const kpis = useMemo(() => [
    {
      label: 'Total Customers',
      value: metrics.total_customers?.toLocaleString() || 0,
      icon: '👥'
    },
    {
      label: 'Active Customers',
      value: metrics.active_customers?.toLocaleString() || 0,
      subtext: `${((metrics.active_customers / metrics.total_customers) * 100).toFixed(1)}%`
    },
    {
      label: 'Churn Rate',
      value: `${(metrics.churn_rate * 100).toFixed(2)}%`,
      icon: '⚠️',
      warning: metrics.churn_rate > 0.4
    },
    {
      label: 'Total Revenue',
      value: `$${(metrics.total_revenue / 1000000).toFixed(1)}M`,
      icon: '💰'
    },
    {
      label: 'Avg Customer LTV',
      value: `$${metrics.avg_customer_ltv?.toLocaleString(undefined, { maximumFractionDigits: 0 })}`,
      icon: '💎'
    }
  ], [metrics]);

  return (
    <div className="dashboard">
      <section className="kpi-grid">
        {kpis.map((kpi, idx) => (
          <div key={idx} className={`kpi-card ${kpi.warning ? 'warning' : ''}`}>
            {kpi.icon && <span className="kpi-icon">{kpi.icon}</span>}
            <div className="kpi-content">
              <p className="kpi-label">{kpi.label}</p>
              <p className="kpi-value">{kpi.value}</p>
              {kpi.subtext && <p className="kpi-subtext">{kpi.subtext}</p>}
            </div>
          </div>
        ))}
      </section>

      <section className="segment-distribution">
        <h2>Customer Segment Distribution</h2>
        <div className="segment-list">
          {metrics.segments?.map((seg, idx) => (
            <div key={idx} className="segment-bar">
              <div className="segment-label">
                <span>{seg.segment}</span>
                <span className="segment-count">{seg.count} customers</span>
              </div>
              <div className="segment-bar-container">
                <div
                  className="segment-bar-fill"
                  style={{ width: `${seg.percentage}%` }}
                />
              </div>
              <span className="segment-percentage">{seg.percentage.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </section>

      <section className="insights">
        <h2>Key Insights</h2>
        <ul className="insights-list">
          <li>
            <strong>Retention Focus:</strong> {((metrics.active_customers / metrics.total_customers) * 100).toFixed(1)}% of customers are still active
          </li>
          <li>
            <strong>At Risk:</strong> {metrics.churned_customers?.toLocaleString()} customers are inactive for 90+ days
          </li>
          <li>
            <strong>Revenue Concentration:</strong> Average customer value is ${metrics.avg_customer_ltv?.toFixed(0)}, with significant variance
          </li>
          <li>
            <strong>Action Items:</strong> Focus on dormant segment ({metrics.segments?.find(s => s.segment === 'Dormant')?.percentage.toFixed(1)}%) and at-risk high-value customers
          </li>
        </ul>
      </section>
    </div>
  );
}
