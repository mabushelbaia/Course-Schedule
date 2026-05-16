import { useState } from "react";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import LinearProgress from "@mui/material/LinearProgress";
import { uploadFile } from "../api";
import type { Course } from "../types";
import FileDropzone from "../components/FileDropzone";
import ScheduleTable from "../components/ScheduleTable";
import DownloadButtons from "../components/DownloadButtons";
import ErrorAlert from "../components/ErrorAlert";

export default function UploadPage() {
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState<Course[] | null>(null);
  const [resultId, setResultId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setLoading(true);
    setError(null);
    setCourses(null);
    try {
      const data = await uploadFile(file);
      setCourses(data.courses);
      setResultId(data.id);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Upload Schedule
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Select an HTML file exported from Ritaj to convert to iCalendar format.
      </Typography>

      <FileDropzone onFile={handleFile} disabled={loading} />

      {loading && <LinearProgress sx={{ mt: 2 }} />}

      {error && <ErrorAlert message={error} onRetry={() => setError(null)} />}

      {courses && (
        <Box mt={3}>
          <Typography variant="h6" mb={1}>Schedule Parsed Successfully</Typography>
          <ScheduleTable courses={courses} />
          <Box mt={2}>
            <DownloadButtons id={resultId!} />
          </Box>
        </Box>
      )}
    </Box>
  );
}
