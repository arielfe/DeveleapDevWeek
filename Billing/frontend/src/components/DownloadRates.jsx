import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
} from "@nextui-org/react";
import axios from "axios";

function DownloadRates() {
  const [responseMessage, setResponseMessage] = useState("");
  const [statusColor, setStatusColor] = useState("gray");

  const handleDownload = async () => {
    try {
      // Request the file from the backend
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/rates`,
        {
          responseType: "blob", // Important for downloading the file
        }
      );

      // Create a link to trigger the download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "rates.xlsx"); // Set the filename
      document.body.appendChild(link);
      link.click(); // Programmatically click the link to trigger the download
      document.body.removeChild(link);

      setResponseMessage("File downloaded successfully.");
      setStatusColor("green");
    } catch (error) {
      console.error("Error downloading rates file:", error);
      setResponseMessage("Failed to download rates file.");
      setStatusColor("red");
    }
  };

  return (
    <Card
      className="border-none rounded-xl shadow-lg"
      style={{
        background: "linear-gradient(135deg, #e0c3fc, #8ec5fc)",
        color: "#fff",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center", // Centers the button vertically
      }}
    >
      <CardHeader className="pb-0">
        <h3 className="text-xl font-semibold text-white">Download Rates</h3>
      </CardHeader>
      <CardBody
        className="pt-0 flex-grow flex justify-center items-center" // Centers the content inside the body
      >
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={handleDownload}
        >
          Download Rates File
        </Button>
      </CardBody>
      <CardFooter className="flex justify-center">
        <div
          className="pt-2 text-center"
          style={{
            minHeight: "40px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            marginTop: "10px",
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

export default DownloadRates;
