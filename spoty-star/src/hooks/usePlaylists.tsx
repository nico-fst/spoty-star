import { useState } from "react";
import { Playlist } from "../types";
import axios from "axios";

export const usePlaylists = () => {
  const [fetchingPlaylists, setFetchingPlaylists] = useState<boolean>(false);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);

  const fetchPlaylists = async () => {
    setFetchingPlaylists(true);
    try {
      const resp = await axios.get<Playlist[]>("/api/get_playlists");
      setPlaylists(resp.data);
    } catch (e: any) {
      if (e.response.status === 401) {
        window.location.href = "/api/login?next=/search";
      }
      console.error("Error fetching data:", e);
    }
    setFetchingPlaylists(false);
  };

  return {
    playlists,
    fetchingPlaylists,
    fetchPlaylists,
  };
};
