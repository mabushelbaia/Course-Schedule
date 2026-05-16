import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import type { Course } from "../types";

export default function ScheduleTable({ courses }: { courses: Course[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600 }}>Course</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Title</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Sec</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Days</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Room</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {courses.map((c, i) => (
            <TableRow key={i}>
              <TableCell sx={{ fontWeight: 600, color: "primary.main" }}>
                {c["Course Label"]}
              </TableCell>
              <TableCell>{c["Course Title"]}</TableCell>
              <TableCell>{c["Section"]}</TableCell>
              <TableCell>{c["Days"]}</TableCell>
              <TableCell>{c["Time"]}</TableCell>
              <TableCell>{c["Room"]}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
