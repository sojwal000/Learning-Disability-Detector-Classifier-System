import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/services';
import './Dashboard.css';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getOverview();
      setAnalytics(data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadgeClass = (riskLevel) => {
    switch (riskLevel) {
      case 'high': return 'badge-danger';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-success';
      default: return 'badge-info';
    }
  };

  if (loading) {
    return <div className="spinner"></div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon students">📚</div>
          <div className="stat-content">
            <h3>{analytics?.total_students || 0}</h3>
            <p>Total Students</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon tests">✍️</div>
          <div className="stat-content">
            <h3>{analytics?.total_tests || 0}</h3>
            <p>Tests Completed</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon high-risk">⚠️</div>
          <div className="stat-content">
            <h3>{analytics?.risk_distribution?.high || 0}</h3>
            <p>High Risk Cases</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon medium-risk">⚡</div>
          <div className="stat-content">
            <h3>{analytics?.risk_distribution?.medium || 0}</h3>
            <p>Medium Risk Cases</p>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Recent Activity</h3>
            </div>
            
            {analytics?.recent_activity && analytics.recent_activity.length > 0 ? (
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Detection Type</th>
                      <th>Risk Level</th>
                      <th>Confidence</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.recent_activity.map((activity, index) => (
                      <tr key={index}>
                        <td>
                          <strong>
                            {activity.prediction_class === 'dyslexia' && 'Dyslexia'}
                            {activity.prediction_class === 'dysgraphia' && 'Dysgraphia'}
                            {activity.prediction_class === 'dyscalculia' && 'Dyscalculia'}
                            {activity.prediction_class === 'none' && 'No Issues'}
                          </strong>
                        </td>
                        <td>
                          <span className={`badge ${getRiskBadgeClass(activity.risk_level)}`}>
                            {activity.risk_level.toUpperCase()}
                          </span>
                        </td>
                        <td>{(activity.confidence * 100).toFixed(1)}%</td>
                        <td>{new Date(activity.predicted_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="p-3">No recent activity</p>
            )}
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Risk Distribution</h3>
            </div>
            <div className="risk-chart">
              <div className="risk-bar">
                <div className="risk-label">Low Risk</div>
                <div className="risk-progress">
                  <div 
                    className="risk-fill low"
                    style={{ width: `${analytics?.risk_distribution?.low || 0}%` }}
                  ></div>
                </div>
                <div className="risk-count">{analytics?.risk_distribution?.low || 0}</div>
              </div>
              
              <div className="risk-bar">
                <div className="risk-label">Medium Risk</div>
                <div className="risk-progress">
                  <div 
                    className="risk-fill medium"
                    style={{ width: `${analytics?.risk_distribution?.medium || 0}%` }}
                  ></div>
                </div>
                <div className="risk-count">{analytics?.risk_distribution?.medium || 0}</div>
              </div>
              
              <div className="risk-bar">
                <div className="risk-label">High Risk</div>
                <div className="risk-progress">
                  <div 
                    className="risk-fill high"
                    style={{ width: `${analytics?.risk_distribution?.high || 0}%` }}
                  ></div>
                </div>
                <div className="risk-count">{analytics?.risk_distribution?.high || 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
