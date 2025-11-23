/**
 * Frontend Configuration
 * Centralized configuration for API endpoints and other settings
 */

// API Base URL - can be overridden by environment variable
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  // Bonafide endpoints
  fetchBonafideRequests: `${API_BASE_URL}/fetch-bonafide-requests`,
  sendBonafideCertificates: `${API_BASE_URL}/send-bonafide-certificates`,

  // NOC endpoints
  fetchNocRequests: `${API_BASE_URL}/noc/fetch-noc-requests`,
  sendNocCertificates: `${API_BASE_URL}/noc/send-noc-certificates`,

  // Rank endpoints
  rankChecker: `${API_BASE_URL}/ranking/rankchecker`,
  sendRankCertificates: `${API_BASE_URL}/ranking/send-rank-certificates`,

  // Scholarship endpoints
  fetchScholarshipRequests: `${API_BASE_URL}/scholarship/fetch-scholarship-requests`,
  sendScholarshipCertificates: `${API_BASE_URL}/scholarship/send-scholarship-certificates`,

  // Placement endpoints
  placementBot: `${API_BASE_URL}/placement/bot`,
  placementQuery: `${API_BASE_URL}/placement/query`,

  // Academic endpoints
  academicCalendar: `${API_BASE_URL}/academic/calendar`,
  exams: `${API_BASE_URL}/academic/exams`,
  holidays: `${API_BASE_URL}/academic/holidays`,
};

export default API_ENDPOINTS;
