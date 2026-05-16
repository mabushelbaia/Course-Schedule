import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import type { CalendarEvent } from "../types";

export default function CalendarTable({ events }: { events: CalendarEvent[] }) {
  const fmt = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  };

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>End Date</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Event</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {events.map((e, i) => (
            <TableRow key={i}>
              <TableCell>{fmt(e.date)}</TableCell>
              <TableCell>{e.end_date ? fmt(e.end_date) : "\u2014"}</TableCell>
              <TableCell>{e.title}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
