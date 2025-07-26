import { useState } from "react";
import { Playlist } from "../types";
import axios from "axios";

interface PlaylistModalProps {
  playlist: Playlist;
  onClose: () => void;
}

function PlaylistModal({ playlist, onClose }: PlaylistModalProps) {
  const [sorting, setSorting] = useState<boolean>(false);
  const [sorted, setSorted] = useState<boolean>(false);
  const [btnCol, setBtnCol] = useState<string>("primary");
  const [imgLoaded, setImgLoaded] = useState<boolean>(false);

  const handleSortClicked = async () => {
    setSorting(true);
    try {
      const encodedPl = encodeURIComponent(playlist.name);
      await axios.get<string>(`/api/sort_playlist_into_decades/${encodedPl}`);
      setBtnCol("success");
    } catch (e: any) {
      // TODO login guard
      console.error("Error sorting playlist:", e);
    } finally {
      setSorting(false);
      setSorted(true);
    }
  };

  return (
    <dialog id="playlist_modal" className="modal">
      <div className="modal-box flex flex-col gap-4">
        {!imgLoaded && <div className="skeleton aspect-square w-full"></div>}
        <img
          className={`rounded-box w-full ${!imgLoaded ? "hidden" : ""}`}
          src={playlist.images[0].url}
          onLoad={() => setImgLoaded(true)}
        />
        <div>
          <h1 className="font-bold text-2xl">{playlist.name}</h1>
          <p className="opacity-50 uppercase">{playlist.tracks.total} tracks</p>
          <p
            className={`py-4 italic ${playlist.description === "" ? "opacity-30" : ""}`}
          >
            {playlist.description || "Playlist has no description"}
          </p>
          <button
            className={`btn btn-${btnCol} w-40`}
            onClick={() => handleSortClicked()}
          >
            {sorting ? (
              <>
                <span className="loading loading-ring loading-xs"></span>
                <span>Sorting</span>
              </>
            ) : sorted ? (
              "Sorted - Sort again?"
            ) : (
              "Sort into decades"
            )}
          </button>
          {sorting && (
            <button
              className="btn btn-error ml-4"
              onClick={() => setSorting(false)}
            >
              Stop
            </button>
          )}
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button onClick={onClose}>close</button>
      </form>
    </dialog>
  );
}

export default PlaylistModal;
