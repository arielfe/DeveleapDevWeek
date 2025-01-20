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

function UploadRates() {
  const [file, setFile] = useState(null); // State to store the file
  const [responseMessage, setResponseMessage] = useState(""); // State to store response
  const [statusColor, setStatusColor] = useState("gray"); // State for status message color

  // Handle file change (when the user selects a file)
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    // Check if the file is an .xlsx file
    if (
      selectedFile &&
      selectedFile.type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) {
      setFile(selectedFile);
    } else {
      setResponseMessage("Please upload a valid .xlsx file.");
      setStatusColor("red");
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!file) {
      setResponseMessage("Please select a file to upload.");
      setStatusColor("red");
      return;
    }

    // Prepare FormData to send file with the 'file' key
    const formData = new FormData();
    formData.append("file", file); // 'file' is the key the backend expects

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/rates`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data", // Ensure this header is set for file upload
          },
        }
      );

      setResponseMessage(
        response.data.message || "Rates uploaded successfully"
      );
      setStatusColor("green");
    } catch (error) {
      console.error("Error uploading rates:", error);
      setResponseMessage(
        error.response?.data?.error || "Failed to upload rates."
      );
      setStatusColor("red");
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
        <h3 className="text-xl font-semibold text-white">Upload Rates</h3>
      </CardHeader>

      {/* CardBody for file input */}
      <CardBody
        className="pt-0 flex justify-center items-center"
        style={{
          height: "200px", // You can adjust the height as needed
          paddingTop: "40px", // Added padding to push the input down slightly
        }}
      >
        <Input
          type="file"
          onChange={handleFileChange}
          fullWidth
          clearable
          className="mb-4"
          accept=".xlsx" // Ensure only .xlsx files can be chosen
        />
      </CardBody>

      {/* CardFooter for status message */}
      <CardFooter className="flex flex-col justify-center items-center">
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={handleSubmit}
        >
          Upload
        </Button>

        {/* Reserved space for status message */}
        <div
          className="pt-2 text-center"
          style={{
            minHeight: "40px", // Reserve 40px height for status text
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            marginTop: "10px", // Add margin-top for spacing between button and status
          }}
        >
          <p className="text-lg" style={{ color: statusColor }}>
            {responseMessage}
          </p>
        </div>
      </CardFooter>
    </Card>
  );
}

export default UploadRates;
