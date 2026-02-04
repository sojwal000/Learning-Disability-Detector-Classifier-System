import React, { useState, useEffect } from 'react';
import { reportService, studentService } from '../services/services';
import './Reports.css';

const Reports = () => {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadStudents();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      loadReports();
    }
  }, [selectedStudent]);

  const loadStudents = async () => {
    try {
      const data = await studentService.getAll();
      setStudents(data);
    } catch (err) {
      console.error('Failed to load students:', err);
    }
  };

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await reportService.getByStudentId(selectedStudent);
      setReports(data);
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedStudent) {
      alert('Please select a student first');
      return;
    }

    try {
      setGenerating(true);
      await reportService.generate(selectedStudent);
      alert('Report generated successfully!');
      loadReports();
    } catch (err) {
      alert('Failed to generate report: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = async (reportId) => {
    try {
      const blob = await reportService.download(reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportId}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download report: ' + (err.response?.data?.detail || err.message));
    }
  };

  const getRiskBadgeClass = (riskScore) => {
    if (riskScore >= 0.6) return 'badge-danger';
    if (riskScore >= 0.35) return 'badge-warning';
    return 'badge-success';
  };

  return (
    <div className="reports-page">
      <h1>Reports</h1>

      <div className="card">
        <h3>Generate Report</h3>
        
        <div className="report-form">
          <div className="form-group">
            <label className="form-label">Select Student</label>
            <select
              className="form-control"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
            >
              <option value="">-- Select Student --</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.first_name} {student.last_name}
                </option>
              ))}
            </select>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleGenerateReport}
            disabled={!selectedStudent || generating}
          >
            {generating ? 'Generating...' : 'Generate New Report'}
          </button>
        </div>
      </div>

      {selectedStudent && (
        <div className="card">
          <h3>Previous Reports</h3>
          
          {loading ? (
            <div className="spinner"></div>
          ) : reports.length > 0 ? (
            <div className="reports-list">
              {reports.map(report => (
                <div key={report.id} className="report-item">
                  <div className="report-info">
                    <div className="report-header">
                      <strong>{report.report_type.toUpperCase()}</strong>
                      <span className={`badge ${getRiskBadgeClass(report.risk_score)}`}>
                        Risk: {(report.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="report-classification">{report.classification}</p>
                    <p className="report-date">
                      Generated: {new Date(report.generated_at).toLocaleString()}
                    </p>
                    
                    {report.indicators && report.indicators.length > 0 && (
                      <div className="report-indicators">
                        <strong>Indicators:</strong>
                        <ul>
                          {report.indicators.map((indicator, idx) => (
                            <li key={idx}>
                              {indicator.category} - {indicator.risk_level} risk
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <button
                    className="btn btn-outline"
                    onClick={() => handleDownloadReport(report.id)}
                  >
                    Download
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p>No reports available for this student.</p>
          )}
        </div>
      )}

      {!selectedStudent && (
        <div className="card text-center">
          <p>Select a student to view and manage their reports.</p>
        </div>
      )}
    </div>
  );
};

export default Reports;
