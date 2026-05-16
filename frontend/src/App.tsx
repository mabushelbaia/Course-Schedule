import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import UploadPage from "./pages/UploadPage";
import LivePage from "./pages/LivePage";
import CalendarPage from "./pages/CalendarPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/live" element={<LivePage />} />
        <Route path="/calendar" element={<CalendarPage />} />
      </Routes>
    </Layout>
  );
}
