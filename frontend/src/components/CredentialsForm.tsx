import { useState, FormEvent } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";

interface Props {
  onSubmit: (username: string, password: string) => void;
  disabled?: boolean;
}

export default function CredentialsForm({ onSubmit, disabled }: Props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (username && password) onSubmit(username, password);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} maxWidth={420}>
      <TextField
        fullWidth
        label="Ritaj Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        margin="normal"
        required
        disabled={disabled}
      />
      <TextField
        fullWidth
        label="Ritaj Password"
        type={showPassword ? "text" : "password"}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        margin="normal"
        required
        disabled={disabled}
        slotProps={{
          input: {
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          },
        }}
      />
      <Button
        type="submit"
        variant="contained"
        fullWidth
        sx={{ mt: 2 }}
        disabled={disabled || !username || !password}
      >
        Fetch Schedule
      </Button>
    </Box>
  );
}
