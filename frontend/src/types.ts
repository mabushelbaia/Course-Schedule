export interface Course {
  "Course Label": string;
  "Course Title": string;
  "Section": string;
  "Days": string;
  "Time": string;
  "Room": string;
}

export interface CalendarEvent {
  date: string;
  end_date: string | null;
  title: string;
}

export interface SemesterInfo {
  name: string;
  start_date: string;
  end_date: string;
}

export interface UploadResponse {
  id: string;
  courses: Course[];
  filename: string;
}

export interface CalendarResponse {
  id: string;
  academic_year: [number, number] | null;
  semester: SemesterInfo | null;
  events: CalendarEvent[];
}
