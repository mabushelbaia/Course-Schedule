import { ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";

const NAV_ITEMS = [
  { label: "Home", path: "/" },
  { label: "Upload", path: "/upload" },
  { label: "Live Fetch", path: "/live" },
  { label: "Calendar", path: "/calendar" },
];

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const tab = NAV_ITEMS.findIndex((item) => item.path === location.pathname);

  return (
    <>
      <AppBar position="sticky" color="inherit" elevation={1}>
        <Toolbar>
          <Typography variant="h6" fontWeight={700} color="primary">
            Course Schedule
          </Typography>
          <Box sx={{ ml: 4 }}>
            <Tabs
              value={tab === -1 ? false : tab}
              onChange={(_, i) => navigate(NAV_ITEMS[i].path)}
              textColor="primary"
              indicatorColor="primary"
            >
              {NAV_ITEMS.map((item) => (
                <Tab key={item.path} label={item.label} />
              ))}
            </Tabs>
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ py: 4 }}>
        {children}
      </Container>
    </>
  );
}
