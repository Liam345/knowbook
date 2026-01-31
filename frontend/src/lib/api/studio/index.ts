/**
 * Studio API - Re-exports all studio feature APIs
 * Educational Note: Centralized exports for clean imports across the app.
 *
 * Import usage:
 *   import { prdsAPI, JobStatus } from '@/lib/api/studio';
 */

import axios from 'axios';
import { API_BASE_URL } from '../client';

// Shared types
export type JobStatus = 'pending' | 'processing' | 'ready' | 'error';

/**
 * Response for API status checks (TTS, Gemini, etc.)
 */
export interface APIStatusResponse {
  success: boolean;
  configured: boolean;
  message?: string;
}

/**
 * Check if Gemini API is configured
 * Educational Note: Shared utility for features that use Gemini Imagen
 */
export async function checkGeminiStatus(): Promise<APIStatusResponse> {
  try {
    const response = await axios.get(`${API_BASE_URL}/studio/gemini/status`);
    return response.data;
  } catch (error) {
    console.error('Error checking Gemini status:', error);
    return { success: false, configured: false };
  }
}

// Re-export all feature APIs and their types
export * from './prds';
export * from './blogs';
export * from './marketingStrategies';
export * from './businessReports';

// Visual content APIs (Module 8)
export * from './mind-maps';
export * from './flow-diagrams';
export * from './infographics';
export * from './wireframes';

// Interactive content APIs (Module 9)
export * from './quizzes';
export * from './flash-cards';
export * from './presentations';

// Media & Code APIs (Module 10)
export * from './audio';
export * from './videos';
export * from './websites';
export * from './components';
export * from './ads';
export * from './emails';
export * from './social-posts';
