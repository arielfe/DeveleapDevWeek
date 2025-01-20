import React from "react";
import DummyCard from "./components/DummyCard";
function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {/* Render multiple DummyCard components */}
        <DummyCard />
        <DummyCard />
        <DummyCard />
        <DummyCard />
        <DummyCard />
        <DummyCard />
      </div>
    </div>
  );
}

export default App;
