import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Input,
} from "@nextui-org/react";
import axios from "axios";

function PostTruck() {
  const [licenseId, setLicenseId] = useState("");
  const [providerId, setProviderId] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [statusColor, setStatusColor] = useState("gray");

  const handleLicenseIdChange = (e) => {
    setLicenseId(e.target.value);
  };

  const handleProviderIdChange = (e) => {
    setProviderId(e.target.value);
  };

  const handleTruckSubmit = async () => {
    if (!licenseId || !providerId) {
      setResponseMessage("License ID and Provider ID are required.");
      setStatusColor("red");
      return;
    }

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/truck`,
        {
          id: licenseId,
          provider_id: providerId,
        }
      );

      setResponseMessage(
        `Truck created successfully: License ID - ${response.data.id}, Provider ID - ${response.data.provider_id}`
      );
      setStatusColor("green");
    } catch (error) {
      console.error("Error creating truck:", error);
      if (error.response?.status === 400) {
        setResponseMessage("Truck already exists.");
        setStatusColor("red");
      } else {
        setResponseMessage("Failed to create truck.");
        setStatusColor("red");
      }
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
        <h3 className="text-xl font-semibold text-white">Create New Truck</h3>
      </CardHeader>
      <CardBody className="pt-0">
        <Input
          label="License ID"
          value={licenseId}
          onChange={handleLicenseIdChange}
          fullWidth
          clearable
          className="mb-4"
        />
        <Input
          label="Provider ID"
          value={providerId}
          onChange={handleProviderIdChange}
          fullWidth
          clearable
          className="mb-4"
        />
      </CardBody>
      <CardFooter className="flex justify-center">
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={handleTruckSubmit}
        >
          Create Truck
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

export default PostTruck;
