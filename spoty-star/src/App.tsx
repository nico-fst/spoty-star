import {
  Link,
  Route,
  BrowserRouter as Router,
  Routes,
  useLocation,
} from "react-router-dom";
import "./App.css";
import SearchScreen from "./screens/SearchScreen";
import { useEffect } from "react";
import fetchPlaylists from "./screens/SearchScreen";

const AppContent = () => {
  const location = useLocation();

  return (
    <div className="p-10">
      <Routes>
        <Route path="/search" element={<SearchScreen />} />
        <Route path="api/login" />
      </Routes>
      {location.pathname === "/" && (
        <>
          <a href="/api/login" className="btn btn-success">
            Spotify Login
          </a>
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
