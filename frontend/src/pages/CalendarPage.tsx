import { useEffect, useState } from "react";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { fetchCalendar } from "../api";
import type { CalendarResponse } from "../types";
import SemesterCard from "../components/SemesterCard";
import CalendarTable from "../components/CalendarTable";
import DownloadButtons from "../components/DownloadButtons";
import ErrorAlert from "../components/ErrorAlert";

export default function CalendarPage() {
  const [data, setData] = useState<CalendarResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchCalendar()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [retry]);

  if (loading) return <Box textAlign="center" py={8}><CircularProgress /></Box>;
  if (error) return <ErrorAlert message={error} onRetry={() => setRetry((p) => p + 1)} />;
  if (!data) return null;

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Academic Calendar
      </Typography>
      {data.academic_year && (
        <Typography variant="body1" color="text.secondary" mb={2}>
          Academic Year {data.academic_year[0]}/{data.academic_year[1]}
        </Typography>
      )}

      {data.semester && <SemesterCard semester={data.semester} />}

      {data.events.length > 0 ? (
        <>
          <CalendarTable events={data.events} />
          <Box mt={2}>
            <DownloadButtons id={data.id} icsLabel="Download Calendar .ics" />
          </Box>
        </>
      ) : (
        <Typography color="text.secondary">No events found.</Typography>
      )}
    </Box>
  );
}
