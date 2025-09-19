import './index.css';
import './tailwind.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from '../pages/Home.jsx';
import Orders from '../pages/Orders.jsx';
import Tracking from '../pages/Tracking.jsx';
import Register from '../pages/Register.jsx';
import Login from '../pages/Login.jsx';
import SellerDashboard from '../pages/SellerDashboard.jsx';
import DeliveryDashboard from '../pages/DeliveryDashboard.jsx';
import WarehouseDashboard from '../pages/WarehouseDashboard.jsx';

function GlassNav({ auth, setAuth }) {
  return (
    <nav className="flex justify-center space-x-6 p-4 backdrop-blur-md bg-white/30 shadow-lg rounded-xl mt-6 mx-auto w-fit border border-white/40">
      <Link to="/" className="px-4 py-2 rounded-xl font-semibold text-blue-700 hover:bg-blue-100 transition">Home</Link>
      <Link to="/orders" className="px-4 py-2 rounded-xl font-semibold text-green-700 hover:bg-green-100 transition">Orders</Link>
      <Link to="/tracking" className="px-4 py-2 rounded-xl font-semibold text-purple-700 hover:bg-purple-100 transition">Tracking</Link>
      {!auth && <Link to="/login" className="px-4 py-2 rounded-xl font-semibold text-gray-700 hover:bg-gray-100 transition">Login</Link>}
      {!auth && <Link to="/register" className="px-4 py-2 rounded-xl font-semibold text-gray-700 hover:bg-gray-100 transition">Register</Link>}
      {auth?.role === 'seller' && <Link to="/seller" className="px-4 py-2 rounded-xl font-semibold text-orange-700 hover:bg-orange-100 transition">Seller</Link>}
      {auth?.role === 'delivery' && <Link to="/delivery" className="px-4 py-2 rounded-xl font-semibold text-yellow-700 hover:bg-yellow-100 transition">Delivery</Link>}
      {auth?.role === 'warehouse' && <Link to="/warehouse" className="px-4 py-2 rounded-xl font-semibold text-teal-700 hover:bg-teal-100 transition">Warehouse</Link>}
      {auth && <button onClick={() => setAuth(null)} className="px-4 py-2 rounded-xl font-semibold text-red-700 hover:bg-red-100 transition">Logout</button>}
    </nav>
  );
}


function App() {
  const [auth, setAuth] = React.useState(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    return token ? { token, role } : null;
  });

  React.useEffect(() => {
    if (auth) {
      localStorage.setItem('token', auth.token);
      localStorage.setItem('role', auth.role);
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
    }
  }, [auth]);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 flex flex-col">
        <GlassNav auth={auth} setAuth={setAuth} />
        <main className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-2xl mx-auto">
            <Routes>
              <Route path="/" element={<Home auth={auth} />} />
              <Route path="/orders" element={<Orders auth={auth} />} />
              <Route path="/tracking" element={<Tracking auth={auth} />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login setAuth={setAuth} />} />
              <Route path="/seller" element={<SellerDashboard auth={auth} />} />
              <Route path="/delivery" element={<DeliveryDashboard auth={auth} />} />
              <Route path="/warehouse" element={<WarehouseDashboard auth={auth} />} />
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