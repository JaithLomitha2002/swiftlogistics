import React, { useState } from 'react';



export default function Orders() {
  const [description, setDescription] = useState('');
  const [client, setClient] = useState('');
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');
  const [processing, setProcessing] = useState(false);
  const [errors, setErrors] = useState({});

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
      const res = await fetch('http://localhost:5000/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ client, description, amount: parseInt(amount) })
      });
      const data = await res.json();
      if (res.ok && data.payment === 'success') {
        setMessage('✅ Payment Successful, Order Submitted');
      } else if (data.error && data.error.toLowerCase().includes('payment')) {
        setMessage('❌ Payment Failed');
      } else {
        setMessage('Failed to submit order.');
      }
    } catch {
      setMessage('Error submitting order.');
    }
    setProcessing(false);
  };

  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="backdrop-blur-md bg-white/40 shadow-xl rounded-2xl p-10 border border-white/30 w-full max-w-lg">
        <h2 className="text-3xl font-bold mb-6 text-blue-700 drop-shadow">Submit an Order</h2>
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
              placeholder="Order Amount"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              required
            />
            {errors.amount && <p className="text-red-500 text-sm mt-1">{errors.amount}</p>}
          </div>
          <button
            className={`w-full px-6 py-3 rounded-xl font-semibold shadow transition text-white ${processing ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'}`}
            type="submit"
            disabled={processing}
          >
            {processing ? 'Processing...' : 'Submit Order'}
          </button>
        </form>
        {message && <p className="mt-6 text-lg font-semibold text-center text-blue-700">{message}</p>}
      </div>
    </div>
  );
}
