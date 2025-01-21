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

function PostProvider() {
  const [providerName, setProviderName] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [statusColor, setStatusColor] = useState("gray");

  const handleProviderNameChange = (e) => {
    setProviderName(e.target.value);
  };

  const handleProviderSubmit = async () => {
    if (!providerName) {
      setResponseMessage("Provider name is required.");
      setStatusColor("red");
      return;
    }

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/provider`,
        { name: providerName }
      );

      setResponseMessage(
        `Provider created successfully: ID - ${response.data.id}, Name - ${response.data.name}`
      );
      setStatusColor("green");
    } catch (error) {
      console.error("Error creating provider:", error);
      if (error.response?.status === 409) {
        setResponseMessage("Provider already exists.");
        setStatusColor("red");
      } else {
        setResponseMessage("Failed to create provider.");
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
        <h3 className="text-xl font-semibold text-white">
          Create New Provider
        </h3>
      </CardHeader>
      <CardBody className="pt-20">
        <Input
          placeholder="Enter provider name"
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
          Create Provider
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

export default PostProvider;
