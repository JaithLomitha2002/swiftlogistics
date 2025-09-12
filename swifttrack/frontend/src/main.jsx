import './index.css';
import './tailwind.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from '../pages/Home.jsx';
import Orders from '../pages/Orders.jsx';
import Tracking from '../pages/Tracking.jsx';

function GlassNav() {
  return (
    <nav className="flex justify-center space-x-6 p-4 backdrop-blur-md bg-white/30 shadow-lg rounded-xl mt-6 mx-auto w-fit border border-white/40">
      <Link to="/" className="px-4 py-2 rounded-xl font-semibold text-blue-700 hover:bg-blue-100 transition">Home</Link>
      <Link to="/orders" className="px-4 py-2 rounded-xl font-semibold text-green-700 hover:bg-green-100 transition">Orders</Link>
      <Link to="/tracking" className="px-4 py-2 rounded-xl font-semibold text-purple-700 hover:bg-purple-100 transition">Tracking</Link>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 flex flex-col">
        <GlassNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-2xl mx-auto">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/tracking" element={<Tracking />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);