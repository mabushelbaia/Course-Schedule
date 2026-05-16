import Button from "@mui/material/Button";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";

interface Props {
  id: string;
  icsLabel?: string;
}

export default function DownloadButtons({ id, icsLabel = "Download .ics" }: Props) {
  return (
    <Button
      variant="contained"
      color="success"
      startIcon={<CloudDownloadIcon />}
      href={`/api/download/${id}`}
    >
      {icsLabel}
    </Button>
  );
}
