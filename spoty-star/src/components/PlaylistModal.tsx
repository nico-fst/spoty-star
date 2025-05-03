import React, { useState } from "react";
import { Playlist } from "../types";
import axios from "axios";

interface PlaylistModalProps {
  playlist: Playlist;
}

function PlaylistModal({ playlist }: PlaylistModalProps) {
  const [sorting, setSorting] = useState(false);

  const handleSortClicked = async () => {
    setSorting(true);
    try {
      const encodedPl = encodeURIComponent(playlist.name);
      const response = await axios.get<string>(`/api/sort_playlist_into_decades/${encodedPl}`);
      console.log(response.data);
    } catch (error) {
      console.error("Error sorting playlist:", error);
    } finally {
      setSorting(false);
    }
  };

  return (
    <dialog id="playlist_modal" className="modal">
      <div className="modal-box flex flex-col gap-4">
        <img
          className="rounded-box"
          src={playlist.images[0].url}
        />
        <div>
          <h1 className="font-bold text-lg">{playlist.name}</h1>
          <p className="opacity-50 uppercase">{playlist.tracks.total} tracks</p>
          <p className="py-4">
            {playlist.description === ""
              ? "Playlist has no description :("
              : playlist.description}
          </p>
          <button className="btn btn-primary" onClick={() => handleSortClicked()}>
            {sorting ? <span className="loading loading-ring loading-xs"></span> : "Sort into decades"}
          </button>
          {sorting &&
            <button className="btn btn-error" onClick={() => setSorting(false)}>
            Stop
            </button>
          }
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button>close</button>
      </form>
    </dialog>
  );
}

export default PlaylistModal;
