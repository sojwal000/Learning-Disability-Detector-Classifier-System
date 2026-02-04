import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { studentService } from '../services/services';
import './Students.css';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    age: '',
    grade: '',
    gender: ''
  });
  const { user } = useAuth();

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      setLoading(true);
      const data = await studentService.getAll();
      setStudents(data);
    } catch (err) {
      setError('Failed to load students');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await studentService.create({
        ...formData,
        teacher_id: user.id,
        age: formData.age ? parseInt(formData.age) : null
      });
      
      setShowModal(false);
      setFormData({
        first_name: '',
        last_name: '',
        age: '',
        grade: '',
        gender: ''
      });
      
      loadStudents();
    } catch (err) {
      alert('Failed to create student: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return <div className="spinner"></div>;
  }

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Students</h1>
        <button 
          onClick={() => setShowModal(true)} 
          className="btn btn-primary"
        >
          + Add Student
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {students.length === 0 ? (
        <div className="card text-center">
          <p>No students found. Add your first student to get started.</p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Age</th>
                <th>Grade</th>
                <th>Gender</th>
                <th>Registered</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td>
                    <strong>{student.first_name} {student.last_name}</strong>
                  </td>
                  <td>{student.age || '-'}</td>
                  <td>{student.grade || '-'}</td>
                  <td>{student.gender || '-'}</td>
                  <td>{new Date(student.created_at).toLocaleDateString()}</td>
                  <td>
                    <Link 
                      to={`/students/${student.id}`} 
                      className="btn btn-outline btn-sm"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New Student</h2>
              <button 
                className="modal-close" 
                onClick={() => setShowModal(false)}
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">First Name *</label>
                <input
                  type="text"
                  name="first_name"
                  className="form-control"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Last Name *</label>
                <input
                  type="text"
                  name="last_name"
                  className="form-control"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Age</label>
                <input
                  type="number"
                  name="age"
                  className="form-control"
                  value={formData.age}
                  onChange={handleInputChange}
                  min="1"
                  max="100"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Grade</label>
                <input
                  type="text"
                  name="grade"
                  className="form-control"
                  value={formData.grade}
                  onChange={handleInputChange}
                  placeholder="e.g., 5th, 10th"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Gender</label>
                <select
                  name="gender"
                  className="form-control"
                  value={formData.gender}
                  onChange={handleInputChange}
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn btn-outline"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Add Student
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Students;
