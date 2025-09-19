import React from "react";

export default function DeliveryDashboard({ auth }) {
  if (!auth || auth.role !== "delivery") return <div>Unauthorized</div>;
  // Example: View assigned deliveries, update status
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Delivery Person Dashboard</h2>
      <p>View and update your assigned deliveries here.</p>
      {/* Add tables and status update actions */}
    </div>
  );
}
