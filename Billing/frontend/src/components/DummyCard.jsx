import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
} from "@nextui-org/react";
import axios from "axios";

function DummyCard() {
  const [healthStatus, setHealthStatus] = useState("Loading...");
  const [statusColor, setStatusColor] = useState("gray");

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

        // Update this line to match the updated API response structure
        const status = response?.data?.status || "Error";
        setHealthStatus(status);

        // Set color based on health status
        setStatusColor(status === "OK" ? "green" : "red");
        console.log("Health status:", status);
        console.log("Status color set to:", status === "OK" ? "green" : "red");
      } catch (error) {
        console.error("Error fetching health status:", error);
        setHealthStatus("Error");
        setStatusColor("red");
      }
    };

    fetchHealthStatus();
  }, []);

  console.log("Environment Variable VITE_API_URL:", process.env.VITE_API_URL);

  return (
    <Card
      className="border-none rounded-xl shadow-lg"
      style={{
        background: "linear-gradient(135deg, #e0c3fc, #8ec5fc)",
        color: "#fff",
      }}
    >
      <CardHeader className="pb-0">
        <h3 className="text-xl font-semibold text-white">Health Check</h3>
      </CardHeader>
      <CardBody className="pt-0">
        <p className={`text-lg font-medium`} style={{ color: statusColor }}>
          Status: {healthStatus}
        </p>
      </CardBody>
      <CardFooter className="flex justify-center">
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={() => window.location.reload()}
        >
          Refresh
        </Button>
      </CardFooter>
    </Card>
  );
}

export default DummyCard;
