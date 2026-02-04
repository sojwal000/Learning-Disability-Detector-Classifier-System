import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Line, Bar } from 'react-chartjs-2';
import api from '../services/api';
import './StudentProgress.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
);

function StudentProgress() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [studentName, setStudentName] = useState('');
  const [progressData, setProgressData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [timelineData, setTimelineData] = useState(null);
  const [selectedTestType, setSelectedTestType] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  const [exportingPDF, setExportingPDF] = useState(false);

  useEffect(() => {
    fetchAllData();
  }, [id, selectedTestType, dateRange]);

  const fetchAllData = async () => {
    try {
      setLoading(true);

      // Debug: Check if token exists
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      console.log('Auth token exists:', !!token);
      console.log('Current user:', userData ? JSON.parse(userData) : null);
      if (!token) {
        alert('You are not logged in. Please log in again.');
        navigate('/login');
        return;
      }

      // Fetch student info
      const studentRes = await api.get(`/students/${id}`);
      setStudentName(`${studentRes.data.first_name} ${studentRes.data.last_name}`);

      // Build query params
      const params = {};
      if (selectedTestType !== 'all') {
        params.test_type = selectedTestType;
      }
      if (dateRange !== 'all') {
        const days = parseInt(dateRange);
        params.days = days;
      }

      // Fetch progress data
      const [progress, comparison, heatmap, timeline] = await Promise.all([
        api.get(`/progress/student/${id}/progress`, { params }),
        api.get(`/progress/student/${id}/comparison`, { params }),
        api.get(`/progress/student/${id}/heatmap`, { params }),
        api.get(`/progress/student/${id}/timeline`, { params })
      ]);

      setProgressData(progress.data);
      setComparisonData(comparison.data);
      setHeatmapData(heatmap.data);
      setTimelineData(timeline.data);
      
      console.log('Progress Data:', progress.data);
      console.log('Comparison Data:', comparison.data);
      console.log('Heatmap Data:', heatmap.data);
      console.log('Timeline Data:', timeline.data);
    } catch (error) {
      console.error('Error fetching progress data:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to load progress data: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    return '➡️';
  };

  const getTrendColor = (trend) => {
    if (trend === 'improving') return '#10b981';
    if (trend === 'declining') return '#ef4444';
    return '#6b7280';
  };

  const handleExportPDF = async () => {
    try {
      setExportingPDF(true);

      // Build query params
      const params = {};
      if (selectedTestType !== 'all') {
        params.test_type = selectedTestType;
      }
      if (dateRange !== 'all') {
        const days = parseInt(dateRange);
        params.days = days;
      }

      const queryString = new URLSearchParams(params).toString();
      const url = `/progress/student/${id}/export-pdf${queryString ? '?' + queryString : ''}`;

      // Fetch PDF
      const response = await api.get(url, { responseType: 'blob' });

      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `progress_report_${studentName.replace(' ', '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('Failed to export PDF report');
    } finally {
      setExportingPDF(false);
    }
  };

  // Line chart for progress over time
  const getProgressChartData = () => {
    if (!progressData || !progressData.progress_over_time) return null;

    const testTypes = [...new Set(progressData.progress_over_time.map(p => p.test_type))];
    const colors = [
      'rgb(59, 130, 246)',
      'rgb(16, 185, 129)',
      'rgb(245, 158, 11)',
      'rgb(239, 68, 68)',
      'rgb(139, 92, 246)',
      'rgb(236, 72, 153)',
      'rgb(14, 165, 233)'
    ];

    const datasets = testTypes.map((testType, idx) => {
      const data = progressData.progress_over_time
        .filter(p => p.test_type === testType)
        .map(p => ({
          x: new Date(p.test_date),
          y: p.avg_score
        }));

      return {
        label: testType.replace('_', ' ').toUpperCase(),
        data: data,
        borderColor: colors[idx % colors.length],
        backgroundColor: colors[idx % colors.length].replace('rgb', 'rgba').replace(')', ', 0.1)'),
        tension: 0.4,
        fill: true
      };
    });

    return {
      datasets: datasets
    };
  };

  const progressChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day'
        },
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Score (%)'
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Progress Over Time'
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
          }
        }
      }
    }
  };

  // Bar chart for comparison with grade average
  const getComparisonChartData = () => {
    if (!comparisonData || !comparisonData.test_types) return null;

    const labels = comparisonData.test_types.map(t => 
      t.test_type.replace('_', ' ').toUpperCase()
    );
    
    const studentScores = comparisonData.test_types.map(t => t.student_avg);
    const gradeScores = comparisonData.test_types.map(t => t.grade_avg);

    return {
      labels: labels,
      datasets: [
        {
          label: 'Student Average',
          data: studentScores,
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1
        },
        {
          label: 'Grade Average',
          data: gradeScores,
          backgroundColor: 'rgba(156, 163, 175, 0.8)',
          borderColor: 'rgb(156, 163, 175)',
          borderWidth: 1
        }
      ]
    };
  };

  const comparisonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Score (%)'
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Performance vs Grade Average'
      }
    }
  };

  // Heatmap visualization
  const renderHeatmap = () => {
    if (!heatmapData || !heatmapData.dimensions) return null;

    const dimensions = heatmapData.dimensions;
    const maxScore = Math.max(...dimensions.map(d => d.score));

    return (
      <div className="heatmap-container">
        <h3>Performance Heatmap</h3>
        <div className="heatmap-grid">
          {dimensions.map((dim, idx) => {
            const intensity = dim.score / maxScore;
            const color = intensity > 0.7 ? '#10b981' : 
                         intensity > 0.4 ? '#f59e0b' : '#ef4444';
            
            return (
              <div 
                key={idx} 
                className="heatmap-cell"
                style={{
                  backgroundColor: color,
                  opacity: 0.3 + (intensity * 0.7)
                }}
              >
                <div className="heatmap-label">{dim.dimension}</div>
                <div className="heatmap-score">{dim.score.toFixed(1)}%</div>
                <div className="heatmap-tests">{dim.test_count} tests</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Timeline view
  const renderTimeline = () => {
    if (!timelineData || !timelineData.timeline) return null;

    return (
      <div className="timeline-container">
        <h3>Assessment Timeline</h3>
        <div className="timeline">
          {timelineData.timeline.map((event, idx) => (
            <div key={idx} className="timeline-event">
              <div className="timeline-date">
                {new Date(event.test_date).toLocaleDateString()}
              </div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="timeline-test-type">
                    {event.test_type.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="timeline-score" style={{
                    color: event.score >= 70 ? '#10b981' : 
                           event.score >= 40 ? '#f59e0b' : '#ef4444'
                  }}>
                    {event.score.toFixed(1)}%
                  </span>
                </div>
                {event.ml_prediction && (
                  <div className="timeline-prediction">
                    <span className="prediction-label">ML Prediction:</span>
                    <span className="prediction-value">
                      {event.ml_prediction.toFixed(1)}% confidence
                    </span>
                  </div>
                )}
                {event.detailed_results && (
                  <div className="timeline-details">
                    {Object.entries(event.detailed_results).slice(0, 3).map(([key, value]) => {
                      // Skip rendering if value is an object or array
                      if (typeof value === 'object' && value !== null) {
                        return null;
                      }
                      return (
                        <span key={key} className="detail-chip">
                          {key}: {typeof value === 'number' ? value.toFixed(1) : value}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading progress data...</div>;
  }

  // Check if student has any test data
  const hasTestData = progressData && 
                      progressData.overall_statistics && 
                      progressData.overall_statistics.total_tests > 0;

  return (
    <div className="student-progress">
      <div className="progress-header">
        <button className="back-button" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <h1>Progress Report: {studentName}</h1>
        <button 
          className="export-button" 
          onClick={handleExportPDF}
          disabled={exportingPDF || !hasTestData}
        >
          {exportingPDF ? '⏳ Generating...' : '📄 Export PDF'}
        </button>
      </div>

      {!hasTestData && (
        <div className="empty-state">
          <h2>📊 No Test Data Available</h2>
          <p>This student hasn't taken any tests yet.</p>
          <p>Submit a test to start tracking progress.</p>
          <button 
            className="btn btn-primary" 
            onClick={() => navigate('/tests/submit')}
          >
            Submit First Test
          </button>
        </div>
      )}

      {hasTestData && (
        <>
      {/* Filters */}
      <div className="progress-filters">
        <div className="filter-group">
          <label>Test Type:</label>
          <select 
            value={selectedTestType} 
            onChange={(e) => setSelectedTestType(e.target.value)}
          >
            <option value="all">All Tests</option>
            <option value="reading">Reading</option>
            <option value="writing">Writing</option>
            <option value="math">Math</option>
            <option value="memory">Memory</option>
            <option value="attention">Attention</option>
            <option value="phonological">Phonological</option>
            <option value="visual_processing">Visual Processing</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Time Range:</label>
          <select 
            value={dateRange} 
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="all">All Time</option>
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last 90 Days</option>
            <option value="180">Last 6 Months</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      {progressData && (
        <div className="summary-cards">
          <div className="summary-card">
            <h3>Overall Average</h3>
            <div className="summary-value">
              {progressData.overall_statistics.average_score.toFixed(1)}%
            </div>
            <div className="summary-label">
              {progressData.overall_statistics.total_tests} tests taken
            </div>
          </div>
          <div className="summary-card">
            <h3>Improvement Rate</h3>
            <div className="summary-value" style={{
              color: getTrendColor(progressData.overall_statistics.trend)
            }}>
              {getTrendIcon(progressData.overall_statistics.trend)}
              {progressData.overall_statistics.improvement_rate.toFixed(1)}%
            </div>
            <div className="summary-label">
              {progressData.overall_statistics.trend}
            </div>
          </div>
          <div className="summary-card">
            <h3>Best Performance</h3>
            <div className="summary-value">
              {progressData.overall_statistics.best_test_type.replace('_', ' ').toUpperCase()}
            </div>
            <div className="summary-label">
              {progressData.overall_statistics.best_score.toFixed(1)}% avg
            </div>
          </div>
        </div>
      )}

      {/* Progress Line Chart */}
      {getProgressChartData() && (
        <div className="chart-section">
          <div className="chart-wrapper" style={{ height: '400px' }}>
            <Line data={getProgressChartData()} options={progressChartOptions} />
          </div>
        </div>
      )}

      {/* Comparison Bar Chart */}
      {getComparisonChartData() && (
        <div className="chart-section">
          <div className="chart-wrapper" style={{ height: '350px' }}>
            <Bar data={getComparisonChartData()} options={comparisonChartOptions} />
          </div>
          {comparisonData && (
            <div className="comparison-summary">
              <p>
                <strong>Overall Percentile:</strong> {comparisonData.overall_percentile.toFixed(1)}th 
                (Student avg: {comparisonData.student_overall_avg.toFixed(1)}%, 
                Grade avg: {comparisonData.grade_overall_avg.toFixed(1)}%)
              </p>
            </div>
          )}
        </div>
      )}

      {/* Heatmap */}
      {renderHeatmap()}

      {/* Timeline */}
      {renderTimeline()}
      </>
      )}
    </div>
  );
}

export default StudentProgress;
