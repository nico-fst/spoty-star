// import { useState } from 'react'
import { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const App = () => {
  const [resp, setResp] = useState<string>("");

  const fetchAPI = async () => {
    try {
      const response = await axios.get<string>("/api/gibdoch");
      console.log(response.data);
      setResp(response.data);
      console.log(resp);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchAPI();
  }, []);

  return (
    <div className="p-10">
      {resp && <div>{resp}</div>}
      <div>Spotiify</div>
      <button className="btn btn-secondary" onClick={() => fetchAPI}>
        Log In
      </button>
    </div>
  );
};

export default App;
