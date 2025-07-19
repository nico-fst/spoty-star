import React, { useEffect, useState } from "react";
import { Playlist } from "../types.ts";
import PlaylistModal from "../components/PlaylistModal.tsx";
import { PlaylistList } from "../components/PlaylistList.tsx";
import { usePlaylists } from "../hooks/usePlaylists.tsx";

export const SearchScreen = () => {
  const [search, setSearch] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist | null>(
    null,
  );

  const { playlists, fetchingPlaylists, fetchPlaylists } = usePlaylists();

  const logout = async () => {
    window.location.href = "/api/logout";
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [search]);

  useEffect(() => {
    fetchPlaylists();
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  useEffect(() => {
    const modal = document.getElementById("playlist_modal");
    if (modal instanceof HTMLDialogElement && selectedPlaylist) {
      modal.showModal();
    }
  }, [selectedPlaylist]);

  return (
    <>
      {/* TODO spread out; Log out to the right, making space for new 'Create playlist for month' */}
      <div>
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
        <button className="btn btn-primary ml-4 w-40" onClick={fetchPlaylists}>
          {fetchingPlaylists ? (
            <span className="loading loading-ring loading-xl"></span>
          ) : (
            "Refresh Playlists"
          )}
        </button>
        <button
          className="btn btn-outline btn-primary ml-4 w-40"
          onClick={logout}
        >
          Log out
        </button>
      </div>

      {selectedPlaylist && <PlaylistModal playlist={selectedPlaylist} />}

      <PlaylistList
        playlists={playlists}
        search={search}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        setSelectedPlaylist={setSelectedPlaylist}
        fetchingPlaylists={fetchingPlaylists}
      />
    </>
  );
};
