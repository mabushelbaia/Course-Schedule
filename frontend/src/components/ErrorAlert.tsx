import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import Button from "@mui/material/Button";

interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ErrorAlert({ message, onRetry }: Props) {
  return (
    <Alert severity="error" sx={{ mt: 2 }}>
      <AlertTitle>Error</AlertTitle>
      {message}
      {onRetry && (
        <Button size="small" onClick={onRetry} sx={{ mt: 1 }}>
          Try Again
        </Button>
      )}
    </Alert>
  );
}
