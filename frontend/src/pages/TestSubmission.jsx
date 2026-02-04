import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { studentService, testService } from '../services/services';
import './TestSubmission.css';

const TestSubmission = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    student_id: '',
    test_type: 'reading',
    time_taken: ''
  });
  
  const [readingData, setReadingData] = useState({
    text_provided: '',
    text_read: ''
  });
  
  const [writingData, setWritingData] = useState({
    prompt: '',
    text_written: ''
  });
  
  const [mathData, setMathData] = useState({
    problems: []
  });
  
  const [memoryData, setMemoryData] = useState({
    items_presented: [],
    items_recalled: []
  });
  
  const [attentionData, setAttentionData] = useState({
    total_trials: 0,
    hits: 0,
    misses: 0,
    false_alarms: 0,
    correct_rejections: 0
  });
  
  const [phonologicalData, setPhonologicalData] = useState({
    tasks: []
  });
  
  const [visualProcessingData, setVisualProcessingData] = useState({
    patterns: []
  });
  
  const [audioFile, setAudioFile] = useState(null);
  const [handwritingFile, setHandwritingFile] = useState(null);
  
  const navigate = useNavigate();

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      const data = await studentService.getAll();
      setStudents(data);
    } catch (err) {
      console.error('Failed to load students:', err);
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
    setLoading(true);

    try {
      let testData = {};
      
      if (formData.test_type === 'reading') {
        testData = {
          ...readingData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      } else if (formData.test_type === 'writing') {
        testData = {
          ...writingData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      } else if (formData.test_type === 'math') {
        testData = {
          ...mathData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      } else if (formData.test_type === 'memory') {
        testData = {
          ...memoryData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      } else if (formData.test_type === 'attention') {
        testData = {
          ...attentionData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      } else if (formData.test_type === 'phonological') {
        testData = {
          ...phonologicalData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      } else if (formData.test_type === 'visual_processing') {
        testData = {
          ...visualProcessingData,
          time_taken: formData.time_taken ? parseInt(formData.time_taken) : 0
        };
      }

      const submitFormData = new FormData();
      submitFormData.append('student_id', formData.student_id);
      submitFormData.append('test_type', formData.test_type);
      submitFormData.append('test_data', JSON.stringify(testData));
      submitFormData.append('time_taken', formData.time_taken || '0');
      
      if (audioFile) {
        submitFormData.append('audio_file', audioFile);
      }
      
      if (handwritingFile) {
        submitFormData.append('handwriting_file', handwritingFile);
      }

      await testService.submit(submitFormData);
      
      alert('Test submitted successfully!');
      navigate(`/students/${formData.student_id}`);
    } catch (err) {
      alert('Failed to submit test: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const addMathProblem = () => {
    setMathData({
      problems: [
        ...mathData.problems,
        {
          question: '',
          correct_answer: '',
          student_answer: '',
          is_correct: false,
          error_type: ''
        }
      ]
    });
  };

  const updateMathProblem = (index, field, value) => {
    const updatedProblems = [...mathData.problems];
    updatedProblems[index][field] = value;
    
    if (field === 'student_answer' || field === 'correct_answer') {
      updatedProblems[index].is_correct = 
        updatedProblems[index].student_answer === updatedProblems[index].correct_answer;
    }
    
    setMathData({ problems: updatedProblems });
  };

  const removeMathProblem = (index) => {
    setMathData({
      problems: mathData.problems.filter((_, i) => i !== index)
    });
  };

  return (
    <div className="test-submission">
      <h1>Submit Test</h1>

      <form onSubmit={handleSubmit} className="test-form">
        <div className="card">
          <h3>Test Information</h3>
          
          <div className="form-group">
            <label className="form-label">Select Student *</label>
            <select
              name="student_id"
              className="form-control"
              value={formData.student_id}
              onChange={handleInputChange}
              required
            >
              <option value="">-- Select Student --</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.first_name} {student.last_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Test Type *</label>
            <select
              name="test_type"
              className="form-control"
              value={formData.test_type}
              onChange={handleInputChange}
              required
            >
              <option value="reading">Reading Test</option>
              <option value="writing">Writing Test</option>
              <option value="math">Math Test</option>
              <option value="memory">Memory Test</option>
              <option value="attention">Attention Test</option>
              <option value="phonological">Phonological Awareness Test</option>
              <option value="visual_processing">Visual Processing Test</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Time Taken (seconds)</label>
            <input
              type="number"
              name="time_taken"
              className="form-control"
              value={formData.time_taken}
              onChange={handleInputChange}
              min="0"
            />
          </div>
        </div>

        {formData.test_type === 'reading' && (
          <div className="card">
            <h3>Reading Test Data</h3>
            
            <div className="form-group">
              <label className="form-label">Text Provided *</label>
              <textarea
                className="form-control"
                value={readingData.text_provided}
                onChange={(e) => setReadingData({...readingData, text_provided: e.target.value})}
                rows="4"
                placeholder="Enter the text that was given to the student to read..."
                required
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">Text Read by Student *</label>
              <textarea
                className="form-control"
                value={readingData.text_read}
                onChange={(e) => setReadingData({...readingData, text_read: e.target.value})}
                rows="4"
                placeholder="Enter what the student actually read..."
                required
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">Audio Recording (Optional)</label>
              <input
                type="file"
                className="form-control"
                accept="audio/*"
                onChange={(e) => setAudioFile(e.target.files[0])}
              />
            </div>
          </div>
        )}

        {formData.test_type === 'writing' && (
          <div className="card">
            <h3>Writing Test Data</h3>
            
            <div className="form-group">
              <label className="form-label">Writing Prompt</label>
              <textarea
                className="form-control"
                value={writingData.prompt}
                onChange={(e) => setWritingData({...writingData, prompt: e.target.value})}
                rows="2"
                placeholder="Enter the writing prompt given to the student..."
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">Student's Written Text *</label>
              <textarea
                className="form-control"
                value={writingData.text_written}
                onChange={(e) => setWritingData({...writingData, text_written: e.target.value})}
                rows="6"
                placeholder="Enter what the student wrote..."
                required
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">Handwriting Image (Optional)</label>
              <input
                type="file"
                className="form-control"
                accept="image/*"
                onChange={(e) => setHandwritingFile(e.target.files[0])}
              />
            </div>
          </div>
        )}

        {formData.test_type === 'math' && (
          <div className="card">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h3>Math Problems</h3>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={addMathProblem}
              >
                + Add Problem
              </button>
            </div>

            {mathData.problems.map((problem, index) => (
              <div key={index} className="math-problem">
                <div className="problem-header">
                  <strong>Problem {index + 1}</strong>
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removeMathProblem(index)}
                  >
                    ✕
                  </button>
                </div>

                <div className="form-group">
                  <label className="form-label">Question</label>
                  <input
                    type="text"
                    className="form-control"
                    value={problem.question}
                    onChange={(e) => updateMathProblem(index, 'question', e.target.value)}
                    placeholder="e.g., What is 15 + 27?"
                  />
                </div>

                <div className="row">
                  <div className="col-6">
                    <div className="form-group">
                      <label className="form-label">Correct Answer</label>
                      <input
                        type="text"
                        className="form-control"
                        value={problem.correct_answer}
                        onChange={(e) => updateMathProblem(index, 'correct_answer', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="col-6">
                    <div className="form-group">
                      <label className="form-label">Student Answer</label>
                      <input
                        type="text"
                        className="form-control"
                        value={problem.student_answer}
                        onChange={(e) => updateMathProblem(index, 'student_answer', e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Error Type (if incorrect)</label>
                  <select
                    className="form-control"
                    value={problem.error_type}
                    onChange={(e) => updateMathProblem(index, 'error_type', e.target.value)}
                  >
                    <option value="">-- Select Error Type --</option>
                    <option value="calculation">Calculation Error</option>
                    <option value="concept">Concept Error</option>
                    <option value="procedure">Procedure Error</option>
                  </select>
                </div>

                {problem.is_correct && (
                  <div className="alert alert-success">✓ Correct Answer</div>
                )}
              </div>
            ))}

            {mathData.problems.length === 0 && (
              <p className="text-center">No problems added yet. Click "Add Problem" to start.</p>
            )}
          </div>
        )}

        {formData.test_type === 'memory' && (
          <div className="card">
            <h3>Memory Test Data</h3>
            
            <div className="form-group">
              <label className="form-label">Items Presented (comma-separated) *</label>
              <textarea
                className="form-control"
                value={memoryData.items_presented.join(', ')}
                onChange={(e) => setMemoryData({
                  ...memoryData,
                  items_presented: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                })}
                rows="3"
                placeholder="e.g., apple, dog, house, tree, book"
                required
              ></textarea>
              <small>Total items: {memoryData.items_presented.length}</small>
            </div>

            <div className="form-group">
              <label className="form-label">Items Recalled by Student (comma-separated) *</label>
              <textarea
                className="form-control"
                value={memoryData.items_recalled.join(', ')}
                onChange={(e) => setMemoryData({
                  ...memoryData,
                  items_recalled: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                })}
                rows="3"
                placeholder="e.g., apple, house, tree"
                required
              ></textarea>
              <small>Total recalled: {memoryData.items_recalled.length}</small>
            </div>

            <div className="alert alert-info">
              Recall accuracy: {memoryData.items_presented.length > 0 
                ? ((memoryData.items_recalled.filter(item => 
                    memoryData.items_presented.includes(item)
                  ).length / memoryData.items_presented.length) * 100).toFixed(1) 
                : 0}%
            </div>
          </div>
        )}

        {formData.test_type === 'attention' && (
          <div className="card">
            <h3>Attention Test Data</h3>
            <p className="text-muted">Continuous Performance Test (CPT) metrics</p>
            
            <div className="row">
              <div className="col-6">
                <div className="form-group">
                  <label className="form-label">Total Trials *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={attentionData.total_trials}
                    onChange={(e) => setAttentionData({
                      ...attentionData,
                      total_trials: parseInt(e.target.value) || 0
                    })}
                    min="0"
                    required
                  />
                </div>
              </div>

              <div className="col-6">
                <div className="form-group">
                  <label className="form-label">Hits (Correct Detections) *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={attentionData.hits}
                    onChange={(e) => setAttentionData({
                      ...attentionData,
                      hits: parseInt(e.target.value) || 0
                    })}
                    min="0"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="row">
              <div className="col-6">
                <div className="form-group">
                  <label className="form-label">Misses (Missed Targets) *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={attentionData.misses}
                    onChange={(e) => setAttentionData({
                      ...attentionData,
                      misses: parseInt(e.target.value) || 0
                    })}
                    min="0"
                    required
                  />
                </div>
              </div>

              <div className="col-6">
                <div className="form-group">
                  <label className="form-label">False Alarms (Incorrect Responses) *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={attentionData.false_alarms}
                    onChange={(e) => setAttentionData({
                      ...attentionData,
                      false_alarms: parseInt(e.target.value) || 0
                    })}
                    min="0"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Correct Rejections *</label>
              <input
                type="number"
                className="form-control"
                value={attentionData.correct_rejections}
                onChange={(e) => setAttentionData({
                  ...attentionData,
                  correct_rejections: parseInt(e.target.value) || 0
                })}
                min="0"
                required
              />
            </div>

            <div className="alert alert-info">
              <strong>Accuracy:</strong> {attentionData.total_trials > 0 
                ? (((attentionData.hits + attentionData.correct_rejections) / attentionData.total_trials) * 100).toFixed(1)
                : 0}%
            </div>
          </div>
        )}

        {formData.test_type === 'phonological' && (
          <div className="card">
            <h3>Phonological Awareness Tasks</h3>
            
            <div className="form-group">
              <label className="form-label">Rhyming Task</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g., cat-hat: correct, dog-log: correct, sun-moon: incorrect"
                onChange={(e) => {
                  const tasks = [...phonologicalData.tasks];
                  tasks[0] = { task_type: 'rhyming', response: e.target.value };
                  setPhonologicalData({ tasks });
                }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Segmentation Task</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g., 'cat' = /k/ /æ/ /t/"
                onChange={(e) => {
                  const tasks = [...phonologicalData.tasks];
                  tasks[1] = { task_type: 'segmentation', response: e.target.value };
                  setPhonologicalData({ tasks });
                }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Blending Task</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g., /d/ /o/ /g/ = dog"
                onChange={(e) => {
                  const tasks = [...phonologicalData.tasks];
                  tasks[2] = { task_type: 'blending', response: e.target.value };
                  setPhonologicalData({ tasks });
                }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Manipulation Task</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g., 'cat' without /k/ = at"
                onChange={(e) => {
                  const tasks = [...phonologicalData.tasks];
                  tasks[3] = { task_type: 'manipulation', response: e.target.value };
                  setPhonologicalData({ tasks });
                }}
              />
            </div>

            <div className="alert alert-info">
              Tasks completed: {phonologicalData.tasks.filter(t => t && t.response).length} / 4
            </div>
          </div>
        )}

        {formData.test_type === 'visual_processing' && (
          <div className="card">
            <h3>Visual Processing Test</h3>
            
            <div className="form-group">
              <label className="form-label">Simple Pattern Recognition</label>
              <div className="row">
                <div className="col-6">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Correct"
                    onChange={(e) => {
                      const patterns = [...visualProcessingData.patterns];
                      if (!patterns[0]) patterns[0] = { type: 'simple', correct: 0, total: 0 };
                      patterns[0].correct = parseInt(e.target.value) || 0;
                      setVisualProcessingData({ patterns });
                    }}
                    min="0"
                  />
                </div>
                <div className="col-6">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Total"
                    onChange={(e) => {
                      const patterns = [...visualProcessingData.patterns];
                      if (!patterns[0]) patterns[0] = { type: 'simple', correct: 0, total: 0 };
                      patterns[0].total = parseInt(e.target.value) || 0;
                      setVisualProcessingData({ patterns });
                    }}
                    min="0"
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Complex Pattern Recognition</label>
              <div className="row">
                <div className="col-6">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Correct"
                    onChange={(e) => {
                      const patterns = [...visualProcessingData.patterns];
                      if (!patterns[1]) patterns[1] = { type: 'complex', correct: 0, total: 0 };
                      patterns[1].correct = parseInt(e.target.value) || 0;
                      setVisualProcessingData({ patterns });
                    }}
                    min="0"
                  />
                </div>
                <div className="col-6">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Total"
                    onChange={(e) => {
                      const patterns = [...visualProcessingData.patterns];
                      if (!patterns[1]) patterns[1] = { type: 'complex', correct: 0, total: 0 };
                      patterns[1].total = parseInt(e.target.value) || 0;
                      setVisualProcessingData({ patterns });
                    }}
                    min="0"
                  />
                </div>
              </div>
            </div>

            {visualProcessingData.patterns.length > 0 && (
              <div className="alert alert-info">
                <div>
                  <strong>Simple Patterns:</strong> {visualProcessingData.patterns[0] && visualProcessingData.patterns[0].total > 0
                    ? ((visualProcessingData.patterns[0].correct / visualProcessingData.patterns[0].total) * 100).toFixed(1)
                    : 0}%
                </div>
                <div>
                  <strong>Complex Patterns:</strong> {visualProcessingData.patterns[1] && visualProcessingData.patterns[1].total > 0
                    ? ((visualProcessingData.patterns[1].correct / visualProcessingData.patterns[1].total) * 100).toFixed(1)
                    : 0}%
                </div>
              </div>
            )}
          </div>
        )}

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-outline"
            onClick={() => navigate(-1)}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit Test'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TestSubmission;
