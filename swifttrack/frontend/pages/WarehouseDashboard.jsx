import React from "react";

export default function WarehouseDashboard({ auth }) {
  if (!auth || auth.role !== "warehouse") return <div>Unauthorized</div>;
  // Example: Assign delivery persons, manage orders
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Warehouse Dashboard</h2>
      <p>Assign delivery persons and manage warehouse orders here.</p>
      {/* Add tables and assignment actions */}
    </div>
  );
}
