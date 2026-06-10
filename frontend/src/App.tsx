import { useState, useEffect } from "react";
import { fetchStatus } from "./services/api";
import HelmsmanDashboard from "./pages/HelmsmanDashboard";
import AGDashboard from "./pages/AGDashboard";

export default function App() {
  const [mode, setMode] = useState<string>("fuzzy");

  useEffect(() => {
    const check = async () => {
      const s = await fetchStatus();
      if (s?.mode) setMode(s.mode);
    };
    check();
    const id = setInterval(check, 5000);
    return () => clearInterval(id);
  }, []);

  return mode === "ag" ? <AGDashboard /> : <HelmsmanDashboard />;
}
