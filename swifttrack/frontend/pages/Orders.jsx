import React, { useState } from 'react';
import axios from 'axios';

// Configure axios base URL
const API_BASE_URL = 'http://localhost:5000/api';

export default function Orders() {
  const [description, setDescription] = useState('');
  const [client, setClient] = useState('');
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');
  const [processing, setProcessing] = useState(false);
  const [errors, setErrors] = useState({});
  const [lastOrderId, setLastOrderId] = useState('');

  const validate = () => {
    const errs = {};
    if (!client.trim()) errs.client = 'Client name is required.';
    if (!description.trim()) errs.description = 'Order description is required.';
    if (!amount || isNaN(amount) || Number(amount) <= 0) errs.amount = 'Amount must be a positive number.';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length) return;

    setMessage('Processing Payment...');
    setProcessing(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/orders`, {
        client: client.trim(),
        description: description.trim(),
        amount: parseInt(amount)
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000 // 10 second timeout
      });

      const data = response.data;
      
      if (response.status === 200 && data.payment === 'success') {
        setMessage(`✅ Payment Successful! Order ${data.order_id} submitted for processing`);
        setLastOrderId(data.order_id);
        
        // Clear form
        setClient('');
        setDescription('');
        setAmount('');
        
        // Show success message for longer
        setTimeout(() => {
          setMessage('');
        }, 5000);
      } else {
        setMessage('❌ Order submission failed');
      }
    } catch (error) {
      console.error('Order submission error:', error);
      
      if (error.response) {
        // Server responded with error status
        const errorData = error.response.data;
        if (errorData.error && errorData.error.toLowerCase().includes('payment')) {
          setMessage('❌ Payment Failed');
        } else {
          setMessage(`❌ Error: ${errorData.error || 'Order submission failed'}`);
        }
      } else if (error.request) {
        // Network error
        setMessage('❌ Network error - please check if the backend is running');
      } else {
        setMessage('❌ Unexpected error occurred');
      }
    }
    
    setProcessing(false);
  };

  const testBackendConnection = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setMessage(`✅ Backend connected: ${response.data.status}`);
    } catch (error) {
      setMessage('❌ Backend connection failed - please start the backend service');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="backdrop-blur-md bg-white/40 shadow-xl rounded-2xl p-10 border border-white/30 w-full max-w-lg">
        <h2 className="text-3xl font-bold mb-6 text-blue-700 drop-shadow">Submit an Order</h2>
        
        {/* Backend connection test button */}
        <div className="mb-4 text-center">
          <button
            onClick={testBackendConnection}
            className="text-sm px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 transition"
          >
            Test Backend Connection
          </button>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <input
              className="border-none outline-none bg-white/60 rounded-xl p-4 w-full text-lg shadow focus:ring-2 focus:ring-blue-300"
              type="text"
              placeholder="Client Name"
              value={client}
              onChange={e => setClient(e.target.value)}
              required
            />
            {errors.client && <p className="text-red-500 text-sm mt-1">{errors.client}</p>}
          </div>
          
          <div>
            <input
              className="border-none outline-none bg-white/60 rounded-xl p-4 w-full text-lg shadow focus:ring-2 focus:ring-blue-300"
              type="text"
              placeholder="Order Description"
              value={description}
              onChange={e => setDescription(e.target.value)}
              required
            />
            {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
          </div>
          
          <div>
            <input
              className="border-none outline-none bg-white/60 rounded-xl p-4 w-full text-lg shadow focus:ring-2 focus:ring-blue-300"
              type="number"
              placeholder="Order Amount (USD)"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              required
              min="1"
            />
            {errors.amount && <p className="text-red-500 text-sm mt-1">{errors.amount}</p>}
          </div>
          
          <button
            className={`w-full px-6 py-3 rounded-xl font-semibold shadow transition text-white ${
              processing ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'
            }`}
            type="submit"
            disabled={processing}
          >
            {processing ? 'Processing Payment...' : 'Submit Order & Process Payment'}
          </button>
        </form>

        {message && (
          <div className="mt-6 p-4 rounded-xl bg-white/60 shadow border border-white/20">
            <p className="text-lg font-semibold text-center text-blue-700">{message}</p>
            {lastOrderId && (
              <p className="text-sm text-center mt-2 text-gray-600">
                Order ID: {lastOrderId}
              </p>
            )}
          </div>
        )}

        {/* Middleware architecture info */}
        <div className="mt-6 p-4 rounded-xl bg-blue-50/60 border border-blue-200/30">
          <h3 className="font-semibold text-blue-800 mb-2">Middleware Processing Flow:</h3>
          <ol className="text-sm text-blue-700 space-y-1">
            <li>1. Payment validation</li>
            <li>2. CMS integration (SOAP/XML)</li>
            <li>3. WMS processing (TCP/IP)</li>
            <li>4. ROS optimization (REST/JSON)</li>
            <li>5. Real-time status updates</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
