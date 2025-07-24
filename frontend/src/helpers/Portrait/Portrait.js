/**
 * Portrait URL helper utilities
 * @module helpers/Portrait/Portrait
 */

import { flattenToAppURL } from '@plone/volto/helpers';

/**
 * Get the correct portrait URL for API endpoints
 * Handles the ++api++ prefix needed for Volto's development proxy
 * 
 * @function getPortraitUrl
 * @param {string} portrait The portrait URL from the API
 * @returns {string|null} The corrected portrait URL or null
 */
export const getPortraitUrl = (portrait) => {
  if (!portrait) return null;
  
  // In development, API URLs need the ++api++ prefix
  if (portrait.includes('/@portrait') && !portrait.includes('/++api++/')) {
    return portrait.replace('/@portrait', '/++api++/@portrait');
  }
  
  return flattenToAppURL(portrait);
};

/**
 * Check if a portrait URL exists and is valid
 * 
 * @function hasPortrait
 * @param {string} portrait The portrait URL
 * @returns {boolean} True if portrait exists
 */
export const hasPortrait = (portrait) => {
  return Boolean(portrait);
};