/**
 * Frontend configuration for the AI Engine UI.
 * This file centralizes all environment-dependent constants.
 */

// Use NEXT_PUBLIC prefix for variables that need to be available in the browser
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// WebSocket URL derived from API_BASE_URL
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

export const CONFIG = {
  API_BASE_URL,
  WS_BASE_URL,
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
};

export default CONFIG;
