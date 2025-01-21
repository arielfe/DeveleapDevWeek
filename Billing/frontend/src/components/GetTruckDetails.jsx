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

export default function GetTruckDetails({ truckId }) {
  const [truckData, setTruckData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fromTime, setFromTime] = useState(""); // Initially set as empty string
  const [toTime, setToTime] = useState(""); // Default to current time

  // Handle from time input change
  const handleFromTimeChange = (e) => {
    setFromTime(e.target.value);
  };

  // Handle to time input change
  const handleToTimeChange = (e) => {
    setToTime(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!fromTime || !toTime) {
      setError("Both 'from' and 'to' date-time values are required.");
      return;
    }

    setLoading(true);
    setError(null);
    setTruckData(null); // Reset truck data before new request

    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/truck/${truckId}`,
        {
          params: {
            from: fromTime,
            to:
              toTime ||
              new Date()
                .toISOString()
                .slice(0, 19)
                .replace(/[-T]/g, "")
                .replace(/:/g, ""),
          },
        }
      );
      setTruckData(response.data); // Set the truck data in state
    } catch (err) {
      setError("Error fetching truck data.");
      console.error("Error fetching truck data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Display loading or error message if needed
  if (loading) return <p>Loading...</p>;

  return (
    <Card
      className="border-none rounded-xl shadow-lg"
      style={{
        background: "linear-gradient(135deg, #e0c3fc, #8ec5fc)",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        height: "100%",
      }}
    >
      <CardHeader className="pb-0">
        <h3 className="text-xl font-semibold text-white">Truck Details</h3>
      </CardHeader>

      <CardBody className="pt-20 flex-grow">
        {/* Date Inputs for from and to */}
        <Input
          placeholder="From (YYYYMMDDHHMMSS)"
          value={fromTime}
          onChange={handleFromTimeChange}
          fullWidth
          clearable
          className="mb-4"
        />
        <Input
          placeholder="To (YYYYMMDDHHMMSS)"
          value={toTime}
          onChange={handleToTimeChange}
          fullWidth
          clearable
          className="mb-4"
        />
      </CardBody>

      <CardFooter className="flex justify-center" style={{ marginTop: "auto" }}>
        <Button
          color="gradient"
          radius="full"
          className="shadow-lg hover:scale-105 transition-transform"
          onClick={handleSubmit}
        >
          Fetch Truck Data
        </Button>
      </CardFooter>

      {/* Show error message below the button if error exists */}
      {error && (
        <CardBody className="pt-2 text-center" style={{ color: "red" }}>
          <p>{error}</p>
        </CardBody>
      )}

      {/* Show truck details in a table if truck data is available */}
      {truckData && (
        <CardBody className="pt-4">
          <table className="min-w-full table-auto border-collapse">
            <thead>
              <tr>
                <th className="border p-2">Field</th>
                <th className="border p-2">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border p-2">Truck ID</td>
                <td className="border p-2">{truckData.id}</td>
              </tr>
              <tr>
                <td className="border p-2">Tara (kg)</td>
                <td className="border p-2">{truckData.tara}</td>
              </tr>
              <tr>
                <td className="border p-2">Sessions</td>
                <td className="border p-2">{truckData.sessions.join(", ")}</td>
              </tr>
            </tbody>
          </table>
        </CardBody>
      )}
    </Card>
  );
}
