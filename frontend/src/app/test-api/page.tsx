'use client';

import { useState } from 'react';

export default function TestAPI() {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setResult('');
    
    try {
      console.log('Testing API connection...');
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = `${API_BASE_URL}/api/v1/auth/providers`;
      
      console.log('Calling:', url);
      console.log('Environment:', {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        API_BASE_URL,
        finalUrl: url
      });
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      
      setResult(`✅ Success: ${JSON.stringify(data, null, 2)}`);
    } catch (error) {
      console.error('API test failed:', error);
      setResult(`❌ Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">API Connection Test</h1>
      
      <button
        onClick={testAPI}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>
      
      {result && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold mb-2">Result:</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
            {result}
          </pre>
        </div>
      )}
      
      <div className="mt-4 text-sm text-gray-600">
        <p>Expected API URL: http://localhost:8000/api/v1/auth/providers</p>
        <p>Environment: {process.env.NEXT_PUBLIC_API_URL || 'undefined'}</p>
      </div>
    </div>
  );
}