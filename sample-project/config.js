/**
 * Sample JavaScript configuration file with intentional security issues.
 * 
 * © 2025 Andrei Antonescu. All rights reserved.
 * Proprietary – not licensed for public redistribution.
 */

// Hardcoded API keys in JavaScript
const apiKey = "sk_test_9876543210abcdefghijklmnop";
const stripeSecret = "sk_live_9876543210abcdefghijklmnop";
const awsAccessKey = "AKIAJEXAMPLEACCESSKEY";
const awsSecretKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLESECRET";

// Database configuration with hardcoded credentials
const dbConfig = {
  host: 'localhost',
  port: 5432,
  username: 'js_app_user',
  password: 'javascript_password_789',
  database: 'js_app_db'
};

// OAuth tokens and authentication
const oauthConfig = {
  google: 'ya29.a0AfH6SMBxExampleJavaScriptOAuthToken',
  facebook: 'EAACEdEose0cBAExampleJavaScriptFacebookToken',
  github: 'ghp_9876543210abcdefghijklmnopqrstuvwxyz'
};

// API configuration with secrets
const apiConfig = {
  stripe: {
    secretKey: 'sk_test_1234567890abcdefghijklmnop',
    publishableKey: 'pk_test_1234567890abcdefghijklmnop'
  },
  twilio: {
    accountSid: 'AC1234567890abcdefghijklmnopqrstuv',
    authToken: '1234567890abcdefghijklmnopqrstuvw'
  },
  sendgrid: {
    apiKey: 'SG.1234567890abcdefghijklmnopqrstuvwxyz.9876543210abcdefghijklmnopqrstuvwxyz'
  }
};

// Connection strings
const mongoConnection = 'mongodb://user:mongopass123@localhost:27017/app';
const redisConnection = 'redis://user:redispass456@localhost:6379/1';

// Function with hardcoded credentials
function connectToDatabase() {
  const username = 'function_user';
  const password = 'function_password_123';
  const host = 'db.example.com';
  
  return `postgresql://${username}:${password}@${host}:5432/app`;
}

// Safe function without issues
function safeFunction() {
  const safeVar = 'This is safe JavaScript code';
  return safeVar;
}

module.exports = {
  dbConfig,
  apiConfig,
  oauthConfig,
  connectToDatabase,
  safeFunction
};