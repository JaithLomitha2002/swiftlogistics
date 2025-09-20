import React from "react";

export default function SellerDashboard({ auth }) {
  if (!auth || auth.role !== "seller") return <div>Unauthorized</div>;
  // Example: Add goods, view orders
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Seller Dashboard</h2>
      <p>Add goods, view/manage your orders here.</p>
      {/* Add forms and tables for goods and orders */}
    </div>
  );
}
