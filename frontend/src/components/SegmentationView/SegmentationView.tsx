import { useState, useEffect } from 'react';
import axios from 'axios';
import '../../styles/SegmentationView.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (window.location.port === '3000' ? 'http://localhost:8000/api' : '/api');

interface SegmentDetail {
  segment_name: string;
  customer_count: number;
  avg_recency: number;
  avg_frequency: number;
  avg_monetary: number;
  avg_churn_score: number;
  churn_percentage: number;
}

export default function SegmentationView() {
  const [segments, setSegments] = useState<SegmentDetail[]>([]);
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSegments();
  }, []);

  const fetchSegments = async () => {
    try {
      setLoading(true);
      const ruleSegments = ['Champions', 'Loyal', 'At_Risk_HighValue', 'Dormant', 'HighEngagement_LowValue', 'Standard'];

      const details = await Promise.all(
        ruleSegments.map(async (segment) => {
          try {
            const detailRes = await axios.get(`${API_BASE_URL}/segments/${segment}/details`);
            return detailRes.data;
          } catch (err) {
            console.warn(`Could not load ${segment} details`);
            return null;
          }
        })
      );

      setSegments(details.filter((d): d is SegmentDetail => d !== null));
    } catch (err) {
      console.error('Failed to fetch segments:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading segments...</div>;

  return (
    <div className="segmentation-view">
      <h1>Customer Segmentation Analysis</h1>

      <div className="segment-info">
        <p>
          Our segmentation uses three complementary methods: <strong>RFM</strong> (Recency/Frequency/Monetary),
          <strong> Behavioral Clustering</strong> (K-means), and <strong>Rule-based</strong> (business logic).
        </p>
      </div>

      <section className="segments-grid">
        {segments.map((segment, idx) => (
          <div
            key={idx}
            className={`segment-card ${selectedSegment === segment.segment_name ? 'selected' : ''}`}
            onClick={() => setSelectedSegment(selectedSegment === segment.segment_name ? null : segment.segment_name)}
          >
            <div className="segment-header">
              <h3>{segment.segment_name}</h3>
              <span className="customer-count">{segment.customer_count.toLocaleString()} 👥</span>
            </div>

            <div className="segment-stats">
              <div className="stat">
                <span className="label">Avg Recency</span>
                <span className="value">{segment.avg_recency.toFixed(0)} days</span>
              </div>
              <div className="stat">
                <span className="label">Avg Frequency</span>
                <span className="value">{segment.avg_frequency.toFixed(1)} purchases</span>
              </div>
              <div className="stat">
                <span className="label">Avg Monetary</span>
                <span className="value">${segment.avg_monetary.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="stat">
                <span className="label">Churn Risk</span>
                <span className="value" style={{ color: segment.avg_churn_score > 0.5 ? '#e74c3c' : '#27ae60' }}>
                  {(segment.avg_churn_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {selectedSegment === segment.segment_name && (
              <div className="segment-details">
                <p className="description">
                  {getSegmentDescription(segment.segment_name)}
                </p>
                <div className="action-items">
                  <h4>Recommended Actions:</h4>
                  <ul>
                    {getActionItems(segment.segment_name).map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        ))}
      </section>
    </div>
  );
}

function getSegmentDescription(segment: string): string {
  const descriptions: Record<string, string> = {
    'Champions': 'Your best customers - high recency, frequency, and monetary value. VIP treatment recommended.',
    'Loyal': 'Consistent repeat customers with good retention. Ideal for loyalty programs.',
    'At_Risk_HighValue': 'High-value customers showing churn signals. Immediate attention needed.',
    'Dormant': 'Inactive customers (90+ days). Opportunity for win-back campaigns.',
    'HighEngagement_LowValue': 'Highly engaged but low spend. Upsell opportunities.',
    'Standard': 'Regular customers with moderate engagement.'
  };
  return descriptions[segment] || 'Segment characteristics';
}

function getActionItems(segment: string): string[] {
  const actions: Record<string, string[]> = {
    'Champions': ['VIP program', 'Exclusive offers', 'Personalized service', 'Retention focus'],
    'Loyal': ['Loyalty rewards', 'Early product access', 'Community events'],
    'At_Risk_HighValue': ['Urgent outreach', 'Special offer', 'Dedicated support', 'Win-back campaign'],
    'Dormant': ['Win-back email', 'Discount incentive', 'Survey feedback'],
    'HighEngagement_LowValue': ['Upsell campaigns', 'Premium tier offers', 'Bundle deals'],
    'Standard': ['Standard campaigns', 'Regular communications']
  };
  return actions[segment] || ['Follow up', 'Re-engage'];
}
