import { useRef, useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";

interface Props {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export default function FileDropzone({ onFile, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (f: File) => {
    if (f.name.toLowerCase().endsWith(".html")) onFile(f);
  };

  return (
    <Box
      sx={{
        border: "2px dashed",
        borderColor: dragOver ? "primary.main" : "#a5d6a7",
        borderRadius: 3,
        p: 6,
        textAlign: "center",
        bgcolor: dragOver ? "primary.light" : "#f1f8e9",
        cursor: disabled ? "default" : "pointer",
        transition: "background-color 0.2s, border-color 0.2s",
      }}
      onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setDragOver(false); if (!disabled && e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".html"
        hidden
        onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
      />
      <Typography variant="h5" color="primary" mb={1}>
        Drag & drop your schedule file here
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        or click to browse
      </Typography>
      <Button variant="contained" disabled={disabled}>Browse Files</Button>
      <Typography variant="caption" color="text.secondary" display="block" mt={2}>
        Accepted: .html only &middot; Max 10MB
      </Typography>
    </Box>
  );
}
