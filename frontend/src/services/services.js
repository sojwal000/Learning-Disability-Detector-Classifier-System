import api from './api';

export const studentService = {
  // Get all students
  getAll: async () => {
    const response = await api.get('/students/');
    return response.data;
  },

  // Get a specific student
  getById: async (id) => {
    const response = await api.get(`/students/${id}`);
    return response.data;
  },

  // Create a new student
  create: async (studentData) => {
    const response = await api.post('/students/', studentData);
    return response.data;
  },

  // Update a student
  update: async (id, studentData) => {
    const response = await api.put(`/students/${id}`, studentData);
    return response.data;
  },

  // Delete a student
  delete: async (id) => {
    await api.delete(`/students/${id}`);
  }
};

export const testService = {
  // Submit a test
  submit: async (formData) => {
    const response = await api.post('/tests/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // Get tests for a student
  getByStudentId: async (studentId) => {
    const response = await api.get(`/tests/student/${studentId}`);
    return response.data;
  },

  // Get a specific test
  getById: async (testId) => {
    const response = await api.get(`/tests/${testId}`);
    return response.data;
  }
};

export const analyticsService = {
  // Get analytics for a student
  getStudentAnalytics: async (studentId) => {
    const response = await api.get(`/analytics/student/${studentId}`);
    return response.data;
  },

  // Get overview analytics
  getOverview: async () => {
    const response = await api.get('/analytics/overview');
    return response.data;
  }
};

export const reportService = {
  // Generate a report for a student
  generate: async (studentId) => {
    const response = await api.post(`/reports/generate/${studentId}`);
    return response.data;
  },

  // Get reports for a student
  getByStudentId: async (studentId) => {
    const response = await api.get(`/reports/student/${studentId}`);
    return response.data;
  },

  // Download a report
  download: async (reportId) => {
    const response = await api.get(`/reports/download/${reportId}`, {
      responseType: 'blob'
    });
    return response.data;
  }
};
