import React, { useEffect, useState } from "react";
import axios from "axios";
import { Playlist } from "../types.ts";
import PlaylistModal from "../components/PlaylistModal.tsx";

const SearchScreen = () => {
  const [fetchingPlaylists, setFetchingPlaylists] = useState(false);
  const [search, setSearch] = useState<string>("");
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist | null>(
    null
  );

  const fetchPlaylists = async () => {
    setFetchingPlaylists(true);
    try {
      const response = await axios.get<Playlist[]>("/api/get_playlists");
      setPlaylists(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    setFetchingPlaylists(false);
  };

  useEffect(() => {
    fetchPlaylists();
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const filteredOptions = playlists
    .filter((option) =>
      option.name.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  useEffect(() => {
    const modal = document.getElementById("playlist_modal");
    if (modal instanceof HTMLDialogElement && selectedPlaylist) {
      modal.showModal();
    }
  }, [selectedPlaylist]);

  return (
    <>
      <label className="input">
        <svg className="h-[1em] opacity-50" viewBox="0 0 24 24">
          <g
            strokeLinejoin="round"
            strokeLinecap="round"
            strokeWidth="2.5"
            fill="none"
            stroke="currentColor"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.3-4.3"></path>
          </g>
        </svg>
        <input
          type="search"
          className="grow"
          placeholder="Search"
          value={search}
          onChange={handleSearchChange}
        />
      </label>

      <button className="btn btn-primary ml-4" onClick={fetchPlaylists}>
        {fetchingPlaylists ? (
          <span className="loading loading-ring loading-xl"></span>
        ) : (
          "Refresh Playlists"
        )}
      </button>

      {(playlists.length > 0 && !fetchingPlaylists) ? (
        <ul className="list bg-base-100 rounded-box shadow-md">
          <li className="p-4 pb-2 text-xs opacity-60 tracking-wide mt-4">
            {filteredOptions.length > 99 ? "99+" : filteredOptions.length}{" "}
            {filteredOptions.length === 1 ? "result" : "results"}
          </li>
          {filteredOptions.map((pl, index) => {
            return (
              <>
                <li className="list-row">
                  <div className="text-4xl font-thin opacity-30 tabular-nums w-20 text-right pr-4">
                    {index + 1}
                  </div>
                  <div>
                    <img
                      className="size-10 rounded-box"
                      src={pl.images[pl.images.length - 1].url}
                    />
                  </div>
                  <div className="list-col-grow">
                    <div>{pl.name}</div>
                    <div className="text-xs uppercase font-semibold opacity-40">
                      {pl.tracks.total} tracks
                    </div>
                  </div>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setSelectedPlaylist(pl)}
                  >
                    Select
                  </button>
                </li>
              </>
            );
          })}
        </ul>
      ) : (
          // Placeholder when loading === fetchingPlaylists
        <ul className="list bg-base-100 rounded-box shadow-md">
          <li className="p-4 pb-2 text-xs opacity-60 tracking-wide mt-4">
            loading...
          </li>
          {[...Array(25)].map((_, index) => {
            return (
              <>
                <li className="list-row">
                  <div className="text-4xl font-thin opacity-30 tabular-nums w-20 text-right pr-4">
                    {index + 1}
                  </div>
                  <div className="skeleton size-10 rounded-box"></div>
                  <div className="list-col-grow">
                    <div className="skeleton h-4 w-48"></div>
                    <div className="skeleton h-3 w-24 mt-1"></div>
                  </div>
                  <button className="btn btn-secondary" disabled>
                    Select
                  </button>
                </li>
              </>
            );
          })}
        </ul>
      )}

      {selectedPlaylist && <PlaylistModal playlist={selectedPlaylist} />}
    </>
  );
};

export default SearchScreen;
