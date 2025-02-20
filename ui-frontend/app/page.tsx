"use client";
import { useState, useEffect } from 'react';

export default function Home() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the name from your FastAPI backend
    fetch('http://localhost:8000/get-name')
        .then(response => response.json())
        .then(data => {
          setName(data.name);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching name:', error);
          setLoading(false);
        });
  }, []);

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900">
            <h1 className="text-4xl font-bold mb-8 text-white">Python Name Display</h1>

            {loading ? (
                <p className="text-white">Loading name from Python backend...</p>
            ) : (
                <div className="p-6 bg-blue-600 rounded-lg shadow-lg">
                    <p className="text-2xl font-bold text-white">Hello, {name}!</p>
                </div>
            )}
        </main>
    );
}