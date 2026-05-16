import { useNavigate } from "react-router-dom";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid2";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Button from "@mui/material/Button";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import LockIcon from "@mui/icons-material/Lock";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";

const FEATURES = [
  {
    icon: <UploadFileIcon sx={{ fontSize: 40 }} />,
    title: "Upload HTML",
    desc: "Upload an HTML schedule file exported from Ritaj and download it as .ics",
    action: "Upload File",
    path: "/upload",
  },
  {
    icon: <LockIcon sx={{ fontSize: 40 }} />,
    title: "Live Fetch",
    desc: "Log into Ritaj via FlareSolverr and fetch your schedule directly",
    action: "Fetch Now",
    path: "/live",
  },
  {
    icon: <CalendarMonthIcon sx={{ fontSize: 40 }} />,
    title: "Academic Calendar",
    desc: "View and download Birzeit's academic calendar with holidays and exam dates",
    action: "View Calendar",
    path: "/calendar",
  },
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <Box>
      <Box textAlign="center" mb={5}>
        <Typography variant="h3" fontWeight={700} gutterBottom>
          Course Schedule to Calendar
        </Typography>
        <Typography variant="body1" color="text.secondary" maxWidth={520} mx="auto">
          Convert your Birzeit University course schedule to iCalendar format —
          upload a file or fetch live from Ritaj.
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {FEATURES.map((f) => (
          <Grid size={{ xs: 12, md: 4 }} key={f.title}>
            <Card
              sx={{
                textAlign: "center",
                py: 3,
                cursor: "pointer",
                transition: "box-shadow 0.2s",
                "&:hover": { boxShadow: 4 },
              }}
              onClick={() => navigate(f.path)}
            >
              <Box color="primary.main" mb={1}>
                {f.icon}
              </Box>
              <CardContent>
                <Typography variant="h6" color="primary" fontWeight={600} gutterBottom>
                  {f.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {f.desc}
                </Typography>
                <Button variant="contained" onClick={() => navigate(f.path)}>
                  {f.action}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
