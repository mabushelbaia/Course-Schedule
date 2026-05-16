import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import type { SemesterInfo } from "../types";

export default function SemesterCard({ semester }: { semester: SemesterInfo }) {
  const start = new Date(semester.start_date).toLocaleDateString("en-GB", {
    day: "numeric", month: "long", year: "numeric",
  });
  const end = new Date(semester.end_date).toLocaleDateString("en-GB", {
    day: "numeric", month: "long", year: "numeric",
  });

  return (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" color="primary">
          Detected Semester: {semester.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Start: {start} &mdash; End: {end}
        </Typography>
      </CardContent>
    </Card>
  );
}
