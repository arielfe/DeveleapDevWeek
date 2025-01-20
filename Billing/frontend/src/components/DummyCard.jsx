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

  console.log("Environment Variable VITE_API_URL:", process.env.VITE_API_URL);

  return (
    <Card
      className="border-none rounded-xl shadow-lg"
      style={{
        background: "linear-gradient(135deg, #e0c3fc, #8ec5fc)",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        height: "100%", // Ensure the card fills the available height
      }}
    >
      <CardHeader className="pb-0">
        <h3 className="text-xl font-semibold text-white">Health Check</h3>
      </CardHeader>

      {/* Button placed inside CardBody */}
      <CardBody
        className="flex justify-center items-center"
        style={{
          flex: 1, // Makes the CardBody take up available space
          display: "flex",
          justifyContent: "center", // Centers the button horizontally
          alignItems: "center", // Centers the button vertically
        }}
      >
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={() => window.location.reload()}
        >
          Refresh
        </Button>
      </CardBody>

      {/* Status text placed inside CardFooter */}
      <CardFooter
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "40px", // Ensure there's space for the status text
        }}
      >
        <p className="text-lg" style={{ color: statusColor }}>
          Status: {healthStatus}
        </p>
      </CardFooter>
    </Card>
  );
}

export default DummyCard;
