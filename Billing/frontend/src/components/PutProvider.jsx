import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Input,
} from "@nextui-org/react";
import axios from "axios";

function PutProvider() {
  const [healthStatus, setHealthStatus] = useState("Loading...");
  const [statusColor, setStatusColor] = useState("gray");
  const [providerId, setProviderId] = useState(""); // Add state for provider ID
  const [providerName, setProviderName] = useState("");
  const [responseMessage, setResponseMessage] = useState("");

  // Fetch the health status from the API
  useEffect(() => {
    const fetchHealthStatus = async () => {
      try {
        console.log("Fetching health status from API...");
        console.log("API URL:", `${import.meta.env.VITE_API_URL}/health`);

        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/health`
        );
        console.log("API Response:", response.data);

        const status = response?.data?.status || "Error";
        setHealthStatus(status);

        setStatusColor(status === "OK" ? "green" : "red");
      } catch (error) {
        console.error("Error fetching health status:", error);
        setHealthStatus("Error");
        setStatusColor("red");
      }
    };

    fetchHealthStatus();
  }, []);

  const handleProviderIdChange = (e) => {
    setProviderId(e.target.value);
  };

  const handleProviderNameChange = (e) => {
    setProviderName(e.target.value);
  };

  const handleProviderSubmit = async () => {
    if (!providerId || !providerName) {
      setResponseMessage("Provider ID and name are required.");
      return;
    }

    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/provider/${providerId}`, // Use providerId from state
        { name: providerName }
      );
      setResponseMessage(`Provider updated: ${response.data}`);
    } catch (error) {
      console.error("Error updating provider:", error);
      setResponseMessage("Failed to update provider.");
    }
  };

  return (
    <Card
      className="border-none rounded-xl shadow-lg"
      style={{
        background: "linear-gradient(135deg, #e0c3fc, #8ec5fc)",
        color: "#fff",
      }}
    >
      <CardHeader className="pb-0">
        <h3 className="text-xl font-semibold text-white">Update Provider</h3>
      </CardHeader>
      <CardBody className="pt-20">
        {/* Input for Provider ID */}
        <Input
          placeholder="Enter Provider ID"
          value={providerId}
          onChange={handleProviderIdChange}
          fullWidth
          clearable
          className="mb-4" // Add margin-bottom to the input
        />

        {/* Input for Provider Name */}
        <Input
          placeholder="Enter Provider Name"
          value={providerName}
          onChange={handleProviderNameChange}
          fullWidth
          clearable
          className="mb-4" // Add margin-bottom to the input
        />
      </CardBody>
      <CardFooter className="flex justify-center">
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={handleProviderSubmit}
        >
          Update Provider
        </Button>
      </CardFooter>
      {/* Reserved space for status message */}
      <div
        className="pt-2 text-center"
        style={{
          minHeight: "40px", // Reserve 40px height for status text
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <p className="text-lg" style={{ color: statusColor }}>
          {responseMessage}
        </p>
      </div>
    </Card>
  );
}

export default PutProvider;
