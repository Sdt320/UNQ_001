import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Attach JWT token automatically if stored
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fieldmind_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (email, password) => {
    const res = await api.post('/api/v1/auth/login', { username: email, password });
    if (res.data.access_token) {
      localStorage.setItem('fieldmind_token', res.data.access_token);
      localStorage.setItem('fieldmind_user', JSON.stringify(res.data));
    }
    return res.data;
  },
  registerCustomer: async (payload) => {
    const res = await api.post('/api/v1/auth/register/customer', payload);
    return res.data;
  },
  registerEmployee: async (payload) => {
    const res = await api.post('/api/v1/auth/register/employee', payload);
    return res.data;
  },
  logout: () => {
    localStorage.removeItem('fieldmind_token');
    localStorage.removeItem('fieldmind_user');
  },
  getCurrentUser: () => {
    const user = localStorage.getItem('fieldmind_user');
    return user ? JSON.parse(user) : null;
  }
};

export const adminService = {
  getPendingWorkers: async () => {
    const res = await api.get('/api/v1/admin/pending-workers');
    return res.data;
  },
  approveWorker: async (userId) => {
    const res = await api.patch(`/api/v1/admin/approve-worker/${userId}`);
    return res.data;
  }
};

export const requestService = {
  createRequest: async (payload) => {
    const res = await api.post('/api/v1/requests/create', payload);
    return res.data;
  },
  getRequestDetails: async (jobId) => {
    const res = await api.get(`/api/v1/requests/${jobId}`);
    return res.data;
  },
  listRecentRequests: async () => {
    const res = await api.get('/api/v1/requests');
    return res.data;
  },
  claimJob: async (jobId, officerId, officerName, officerPhone) => {
    const res = await api.post(`/api/v1/requests/${jobId}/claim`, {
      officer_id: officerId,
      officer_name: officerName || 'Marcus Vance',
      officer_phone: officerPhone || '+14155559821'
    });
    return res.data;
  }
};

export const rewardsService = {
  getLeaderboard: async () => {
    const res = await api.get('/api/v1/rewards/leaderboard');
    return res.data;
  },
  getReviews: async () => {
    const res = await api.get('/api/v1/rewards/reviews');
    return res.data;
  },
  submitReview: async (payload) => {
    const res = await api.post('/api/v1/rewards/reviews', payload);
    return res.data;
  }
};

export const webhookService = {
  simulateWhatsAppAccept: async (jobId, fromPhone = "14155559821") => {
    const payload = {
      entry: [{
        changes: [{
          value: {
            messages: [{
              from: fromPhone,
              id: `wamid.HBgLM_${job_id_slice(jobId)}`,
              type: "interactive",
              interactive: {
                type: "button_reply",
                button_reply: {
                  id: `ACCEPT_${jobId}`,
                  title: "Accept Job"
                }
              }
            }]
          }
        }]
      }]
    };
    const res = await api.post('/webhooks/whatsapp', payload);
    return res.data;
  }
};

function job_id_slice(id) {
  return id ? id.slice(0, 8) : 'test';
}
