import React from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
} from "@nextui-org/react";

function DownloadRates() {
  const handleDownload = () => {
    // Trigger the file download by navigating to the backend endpoint
    window.location.href = `${import.meta.env.VITE_API_URL}/rates`;
  };

  return (
    <Card
      className="border-none rounded-xl shadow-lg"
      style={{
        background: "linear-gradient(135deg, #e0c3fc, #8ec5fc)",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center", // Centers the content vertically
        height: "100%",
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
        {/* Optional: status message, but no need for it if backend handles it */}
      </CardFooter>
    </Card>
  );
}

export default DownloadRates;
