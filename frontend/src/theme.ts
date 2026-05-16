import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#2e7d32",
      light: "#e8f5e9",
    },
    background: {
      default: "#f8faf8",
    },
  },
  shape: {
    borderRadius: 8,
  },
});

export default theme;
