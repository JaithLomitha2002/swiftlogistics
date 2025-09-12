


import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="backdrop-blur-md bg-white/40 shadow-xl rounded-2xl p-10 border border-white/30 w-full max-w-lg text-center">
        <h1 className="text-5xl font-extrabold mb-4 text-blue-700 drop-shadow">Welcome to SwiftTrack</h1>
        <p className="text-lg mb-8 text-gray-700">Efficient logistics management made simple.</p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            className="px-6 py-3 rounded-xl bg-green-500 text-white font-semibold shadow hover:bg-green-600 transition"
            onClick={() => navigate('/orders')}
          >
            Place an Order
          </button>
          <button
            className="px-6 py-3 rounded-xl bg-purple-500 text-white font-semibold shadow hover:bg-purple-600 transition"
            onClick={() => navigate('/tracking')}
          >
            Track Orders
          </button>
        </div>
      </div>
    </div>
  );
}
