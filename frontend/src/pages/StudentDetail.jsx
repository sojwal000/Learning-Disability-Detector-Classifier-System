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

  // Generate feedback from features if detailed_feedback doesn't exist
  const generateFeedbackFromFeatures = (features, testType, testData) => {
    const feedback = {
      errors: [],
      skipped: [],
      concerns: []
    };

    if (!features) return feedback;

    // Check for common issues across all test types
    const accuracy = features.accuracy || features.recall_accuracy || 100;
    if (accuracy < 75) {
      feedback.concerns.push(`Performance below expected level: ${accuracy.toFixed(0)}%`);
    }

    // Writing test specific - with detailed comparison
    if (testType === 'writing' && testData) {
      const prompt = testData.prompt || '';
      // Check both possible field names
      const studentText = testData.text_written || testData.student_text || '';
      
      if (prompt && studentText) {
        // Find what words are missing from the end
        const promptWords = prompt.trim().split(/\s+/);
        const studentWords = studentText.trim().split(/\s+/);
        
        if (studentWords.length < promptWords.length) {
          const missingWords = promptWords.slice(studentWords.length).join(' ');
          if (missingWords) {
            feedback.skipped.push(`Did not write: "${missingWords}"`);
          }
          
          const completionRate = (studentWords.length / promptWords.length * 100);
          feedback.concerns.push(`Only wrote ${studentWords.length} out of ${promptWords.length} words (${completionRate.toFixed(0)}%)`);
        }
      }
      
      if (features.spelling_errors > 0) {
        feedback.errors.push(`${features.spelling_errors} spelling error(s) detected`);
      }
      if (features.grammar_errors > 0) {
        feedback.errors.push(`${features.grammar_errors} grammar error(s) found`);
      }
      if (features.letter_reversals > 0) {
        feedback.errors.push(`${features.letter_reversals} letter reversal(s) detected`);
      }
      if (features.inconsistent_spacing > 0) {
        feedback.concerns.push('Inconsistent spacing between words');
      }
    }

    // Reading test specific
    if (testType === 'reading') {
      if (features.reversed_letters > 0) {
        feedback.errors.push(`${features.reversed_letters} letter reversal(s) during reading`);
      }
      if (features.letter_confusions > 0) {
        feedback.errors.push(`${features.letter_confusions} letter confusion(s) observed`);
      }
      if (features.reading_speed && features.reading_speed < 100) {
        feedback.concerns.push(`Reading speed below average (${features.reading_speed.toFixed(0)} wpm)`);
      }
      if (features.error_rate > 10) {
        feedback.concerns.push(`High error rate: ${features.error_rate.toFixed(0)}%`);
      }
    }

    // Math test specific - with detailed problem tracking
    if (testType === 'math' && testData) {
      const problems = testData.problems || [];
      const answers = testData.answers || [];
      
      if (answers.length < problems.length) {
        const skippedCount = problems.length - answers.length;
        feedback.skipped.push(`Did not attempt ${skippedCount} problem(s)`);
        
        // Show which problems were skipped - handle object or string
        for (let i = answers.length; i < Math.min(problems.length, answers.length + 3); i++) {
          const problem = problems[i];
          let problemText = '';
          
          if (typeof problem === 'object' && problem !== null) {
            problemText = problem.question || problem.text || problem.problem || JSON.stringify(problem);
          } else {
            problemText = String(problem);
          }
          
          if (problemText.length > 50) {
            problemText = problemText.substring(0, 50) + '...';
          }
          feedback.skipped.push(`Problem ${i + 1}: "${problemText}"`);
        }
      }
      
      if (features.calculation_errors > 0) {
        feedback.errors.push(`${features.calculation_errors} calculation error(s)`);
      }
      if (features.sign_errors > 0) {
        feedback.errors.push(`${features.sign_errors} sign error(s) (positive/negative confusion)`);
      }
      if (features.place_value_errors > 0) {
        feedback.errors.push(`${features.place_value_errors} place value error(s)`);
      }
      if (features.completion_rate && features.completion_rate < 0.8) {
        feedback.concerns.push(`Only ${(features.completion_rate * 100).toFixed(0)}% of problems completed`);
      }
    }

    // Memory/Attention tests
    if (features.false_recalls > 0) {
      feedback.errors.push(`${features.false_recalls} false recall(s) or incorrect identification(s)`);
    }

    if (features.recall_rate && features.recall_rate < 0.8) {
      feedback.skipped.push(`Only ${(features.recall_rate * 100).toFixed(0)}% of items completed or recalled`);
    }

    return feedback;
  };

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
            <h3>Detailed Feedback</h3>
            {tests.length > 0 ? (
              <div className="feedback-section">
                {(() => {
                  // Get the most recent test (tests should be sorted by date desc)
                  const latestTest = tests[0];
                  const feedback = latestTest.features?.detailed_feedback || 
                                   generateFeedbackFromFeatures(latestTest.features, latestTest.test_type, latestTest.test_data);
                  
                  const hasContent = feedback.errors.length > 0 || feedback.skipped.length > 0 || feedback.concerns.length > 0;
                  
                  return (
                    <>
                      <p className="feedback-test-info">
                        📝 Feedback for most recent test: <strong>{latestTest.test_type.charAt(0).toUpperCase() + latestTest.test_type.slice(1)}</strong> 
                        {' '}({new Date(latestTest.completed_at).toLocaleDateString()})
                      </p>
                      
                      {!hasContent ? (
                        <p className="feedback-success">✅ Great work! No significant issues detected.</p>
                      ) : (
                        <>
                          {feedback.errors.length > 0 && (
                            <div className="feedback-group">
                              <h4 className="feedback-title error">❌ Errors Found</h4>
                              <ul className="feedback-list">
                                {feedback.errors.map((error, index) => (
                                  <li key={index}>{error}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {feedback.skipped.length > 0 && (
                            <div className="feedback-group">
                              <h4 className="feedback-title skipped">⏭️ Skipped Items</h4>
                              <ul className="feedback-list">
                                {feedback.skipped.map((item, index) => (
                                  <li key={index}>{item}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {feedback.concerns.length > 0 && (
                            <div className="feedback-group">
                              <h4 className="feedback-title concern">⚠️ Areas of Concern</h4>
                              <ul className="feedback-list">
                                {feedback.concerns.map((concern, index) => (
                                  <li key={index}>{concern}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </>
                      )}
                    </>
                  );
                })()}
              </div>
            ) : (
              <p>Complete a test to see detailed feedback</p>
            )}
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
