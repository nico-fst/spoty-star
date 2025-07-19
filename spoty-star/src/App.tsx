import {
  Link,
  Route,
  BrowserRouter as Router,
  Routes,
  useLocation,
} from "react-router-dom";
import "./App.css";
import { SearchScreen } from "./screens/SearchScreen";
import axios from "axios";
import { useEffect, useState } from "react";

const AppContent = () => {
  const location = useLocation();
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    const isLoggedIn = async () => {
      try {
        const resp = await axios.get<string>("/api/loggedin");
        return resp.status === 200;
      } catch {
        setLoggedIn(false);
      }
    };

    isLoggedIn();
  }, []);

  return (
    <div className="p-10">
      <Routes>
        <Route path="/search" element={<SearchScreen />} />
        <Route path="api/login" />
      </Routes>
      {location.pathname === "/" && (
        <>
          {loggedIn === false && (
            <a href="/api/login" className="btn btn-success">
              Spotify Login
            </a>
          )}
          <Link to="/search" className="btn btn-success">
            Search
          </Link>
        </>
      )}
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
