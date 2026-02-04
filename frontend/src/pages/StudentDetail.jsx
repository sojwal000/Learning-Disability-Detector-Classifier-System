import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { studentService, testService, analyticsService } from '../services/services';
import './StudentDetail.css';

const StudentDetail = () => {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [tests, setTests] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadStudentData();
  }, [id]);

  const loadStudentData = async () => {
    try {
      setLoading(true);
      const [studentData, testsData, analyticsData] = await Promise.all([
        studentService.getById(id),
        testService.getByStudentId(id),
        analyticsService.getStudentAnalytics(id)
      ]);
      
      setStudent(studentData);
      setTests(testsData);
      setAnalytics(analyticsData);
    } catch (err) {
      setError('Failed to load student data');
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

  if (!student) {
    return <div className="alert alert-error">Student not found</div>;
  }

  return (
    <div className="student-detail">
      <div className="page-header">
        <Link to="/students" className="back-link">← Back to Students</Link>
      </div>

      <div className="student-header-card">
        <div className="student-avatar">
          {student.first_name.charAt(0)}{student.last_name.charAt(0)}
        </div>
        <div className="student-info">
          <h1>{student.first_name} {student.last_name}</h1>
          <div className="student-meta">
            <span>Age: {student.age || 'N/A'}</span>
            <span>•</span>
            <span>Grade: {student.grade || 'N/A'}</span>
            <span>•</span>
            <span>Gender: {student.gender || 'N/A'}</span>
          </div>
        </div>
        <Link to={`/students/${id}/progress`} className="btn-progress">
          📊 View Progress Report
        </Link>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'tests' ? 'active' : ''}`}
          onClick={() => setActiveTab('tests')}
        >
          Tests ({tests.length})
        </button>
        <button
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          Analytics
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="tab-content">
          <div className="row">
            <div className="col-6">
              <div className="card">
                <h3>Quick Stats</h3>
                <div className="stats-list">
                  <div className="stat-item">
                    <span className="stat-label">Total Tests</span>
                    <span className="stat-value">{analytics?.total_tests || 0}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Average Score</span>
                    <span className="stat-value">{analytics?.avg_score || 0}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-6">
              <div className="card">
                <h3>Risk Summary</h3>
                {analytics?.risk_summary && Object.keys(analytics.risk_summary).map(category => {
                  const data = analytics.risk_summary[category];
                  if (data.count === 0) return null;
                  
                  return (
                    <div key={category} className="risk-item">
                      <div className="risk-header">
                        <strong>{category.charAt(0).toUpperCase() + category.slice(1)}</strong>
                        <span className={`badge ${getRiskBadgeClass(data.max_risk)}`}>
                          {data.max_risk.toUpperCase()}
                        </span>
                      </div>
                      <p>Detected {data.count} time(s) with {(data.avg_confidence * 100).toFixed(1)}% confidence</p>
                    </div>
                  );
                })}
                
                {!analytics?.risk_summary || 
                 Object.values(analytics.risk_summary).every(d => d.count === 0) && (
                  <p>No risk indicators detected</p>
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Recent Tests</h3>
            {tests.slice(0, 5).length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Test Type</th>
                    <th>Score</th>
                    <th>Errors</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {tests.slice(0, 5).map(test => (
                    <tr key={test.id}>
                      <td>
                        <strong>{test.test_type.charAt(0).toUpperCase() + test.test_type.slice(1)}</strong>
                      </td>
                      <td>{test.score?.toFixed(1)}%</td>
                      <td>{test.errors}</td>
                      <td>{new Date(test.completed_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No tests completed yet</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'tests' && (
        <div className="tab-content">
          <div className="card">
            {tests.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Test Type</th>
                    <th>Score</th>
                    <th>Errors</th>
                    <th>Time Taken</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {tests.map(test => (
                    <tr key={test.id}>
                      <td>{test.id}</td>
                      <td>
                        <strong>{test.test_type.charAt(0).toUpperCase() + test.test_type.slice(1)}</strong>
                      </td>
                      <td>{test.score?.toFixed(1)}%</td>
                      <td>{test.errors}</td>
                      <td>{test.time_taken ? `${test.time_taken}s` : 'N/A'}</td>
                      <td>{new Date(test.completed_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No tests completed yet</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="tab-content">
          <div className="card">
            <h3>Performance Over Time</h3>
            {analytics?.test_history && analytics.test_history.length > 0 ? (
              <div className="performance-chart">
                {analytics.test_history.map((test, index) => (
                  <div key={index} className="performance-item">
                    <div className="performance-date">
                      {new Date(test.completed_at).toLocaleDateString()}
                    </div>
                    <div className="performance-bar-container">
                      <div 
                        className="performance-bar"
                        style={{ 
                          width: `${test.score}%`,
                          backgroundColor: test.score >= 80 ? '#4CAF50' : 
                                         test.score >= 60 ? '#FF9800' : '#F44336'
                        }}
                      >
                        <span className="performance-score">{test.score.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="performance-type">{test.test_type}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No test history available</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDetail;
