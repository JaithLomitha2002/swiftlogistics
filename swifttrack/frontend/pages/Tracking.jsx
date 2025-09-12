import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');



export default function Tracking() {
  const [status, setStatus] = useState('Waiting for updates...');
  const [paymentStatus, setPaymentStatus] = useState('');

  useEffect(() => {
    socket.on('status_update', (data) => {
      setStatus(data.status);
    });
    socket.on('payment_status', (data) => {
      setPaymentStatus(data.payment_status);
    });
    return () => {
      socket.off('status_update');
      socket.off('payment_status');
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="backdrop-blur-md bg-white/40 shadow-xl rounded-2xl p-10 border border-white/30 w-full max-w-lg text-center">
        <h2 className="text-3xl font-bold mb-6 text-purple-700 drop-shadow">Order Tracking</h2>
        <div className="mb-6">
          <div className="rounded-xl p-6 bg-white/60 shadow border border-white/20">
            <p className="text-lg font-semibold text-blue-700">Delivery Status:</p>
            <p className="text-xl mt-2">{status}</p>
          </div>
        </div>
        {paymentStatus && (
          <div className="rounded-xl p-6 bg-white/60 shadow border border-white/20 mt-4">
            <p className="text-lg font-semibold text-green-700">Payment Status:</p>
            <p className="text-xl mt-2">{paymentStatus}</p>
          </div>
        )}
      </div>
    </div>
  );
}
