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

  const createMonthlist = async (
    yearmonth: string,
  ): Promise<Playlist | null> => {
    try {
      const year = yearmonth.slice(0, 4);
      const month = yearmonth.slice(5, 7);
      console.log("Creating monthlist for:", year, month);
      // todo get -> post in backend
      const resp = await axios.get(`/api/create_monthlist/${year}/${month}`);
      if (resp.status === 201) {
        console.log("Monthlist created successfully");
        await fetchPlaylists();
        return resp.data as Playlist;
      }
    } catch (e: any) {
      if (e.response.status === 400) {
        console.error("ERROR creating monthlist: Playlist already exists");
      } else if (e.response.status === 500) {
        console.error(
          "ERROR creating monthlist: requests.HTTPError in Backend: ",
          e,
        );
      } else {
        console.error("ERROR creating monthlist: ", e);
      }
    }
    return null;
  };

  const checkIfMonthlistExists = async (
    playlistName: string,
  ): Promise<boolean | null> => {
    if (!/^[1-2]\d{3}-\d{2}$/.test(playlistName)) {
      console.log("PlaylistName NOT valid; aborting...");
      return null; // prevent unnecessary calls
    } else {
      console.log("PlaylistName valid; testing if playlist already exists...");
    }

    try {
      const resp = await axios.get(`/api/does_monthlist_exist/${playlistName}`);
      console.log(
        `${playlistName} does exist: ${resp.data} -> ${resp.data === true}`,
      );
      return resp.data === true;
    } catch (e) {
      console.error("Fehler beim Prüfen, ob Playlist existiert:", e);
      return null;
    }
  };

  return {
    playlists,
    fetchingPlaylists,
    fetchPlaylists,
    createMonthlist,
    checkIfMonthlistExists,
  };
};
