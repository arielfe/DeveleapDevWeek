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

function UpdateTruck() {
  const [truckId, setTruckId] = useState("");
  const [providerId, setProviderId] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [statusColor, setStatusColor] = useState("gray");

  const handleTruckIdChange = (e) => {
    setTruckId(e.target.value);
  };

  const handleProviderIdChange = (e) => {
    setProviderId(e.target.value);
  };

  const handleTruckSubmit = async () => {
    if (!truckId || !providerId) {
      setResponseMessage("Truck ID and Provider ID are required.");
      setStatusColor("red");
      return;
    }

    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/truck/${truckId}`, // Use truckId from state
        { provider_id: providerId }
      );

      setResponseMessage(response.data.message);
      setStatusColor("green");
    } catch (error) {
      console.error("Error updating truck:", error);
      if (error.response?.status === 404) {
        setResponseMessage(error.response.data.error);
        setStatusColor("red");
      } else {
        setResponseMessage("Failed to update truck.");
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
        <h3 className="text-xl font-semibold text-white">Update Truck</h3>
      </CardHeader>
      <CardBody className="pt-20">
        <Input
          placeholder="Truck ID"
          value={truckId}
          onChange={handleTruckIdChange}
          fullWidth
          clearable
          className="mb-4"
        />
        <Input
          placeholder="New Provider ID"
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
          Update Truck
        </Button>
      </CardFooter>
      {/* Reserved space for status message */}
      <div
        className="pt-2 text-center"
        style={{
          minHeight: "40px", // Reserve space for status text
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

export default UpdateTruck;
