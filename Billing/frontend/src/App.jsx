import React from "react";
import DummyCard from "./components/DummyCard";
import PutProvider from "./components/PutProvider";
import PostProvider from "./components/PostProvider";
import PostTruck from "./components/PostTruck";
import UpdateTruck from "./components/UpdateTruck";
import UploadRates from "./components/UploadRates";
import DownloadRates from "./components/DownloadRates";

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-500">
        Billing Dashboard
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {/* Render multiple DummyCard components */}
        <DummyCard />
        <PutProvider />
        <PostProvider />
        <PostTruck />
        <UpdateTruck />
        <UploadRates />
        <DownloadRates />
      </div>
    </div>
  );
}

export default App;
