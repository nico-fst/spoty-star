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

  const [monthlistName, setMonthlistName] = useState<string>("");
  const [validMonthlistName, setValidMonthlistName] = useState<boolean>(true);
  const [validatingMonthlistInput, setValidatingMonthlistInput] =
    useState<boolean>(false);
  const [playlistExistsAlready, setPlaylistExistsAlready] =
    useState<boolean>(false);
  const [createdMonthlist, setCreatedMonthlist] = useState<boolean>(false);

  const {
    playlists,
    fetchingPlaylists,
    fetchPlaylists,
    createMonthlist,
    checkIfMonthlistExists,
  } = usePlaylists();

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

  const handleMonthlistNameChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setValidatingMonthlistInput(true);
    setCreatedMonthlist(false);

    setMonthlistName(e.target.value);

    // guard: only proceed if valid monthlist name
    if (!/^[1-2]\d{3}-\d{2}$/.test(e.target.value)) {
      console.log("PlaylistName NOT valid; aborting...");
      setValidMonthlistName(false);
    } else {
      setValidMonthlistName(true);
      const exists = await checkIfMonthlistExists(e.target.value);
      setPlaylistExistsAlready(exists === true);
    }
    setValidatingMonthlistInput(false);
  };

  const onCreateMonthlistBtnClick = async () => {
    const res: { playlist: Playlist } | { error: number } =
      await createMonthlist(monthlistName);
    if ("playlist" in res) {
      setCreatedMonthlist(true);
      setMonthlistName("");
      setValidMonthlistName(true);
      setPlaylistExistsAlready(false);
    } else {
      // TODO handle 400, 401, 500 from backend
    }
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
          {/* Search icon */}
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
          {/* actual input */}
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

      <div className="mt-4">
        <label className="input validator">
          <input
            type="text"
            className="grow"
            placeholder="e.g. 2025-05"
            value={monthlistName}
            onChange={handleMonthlistNameChange}
            pattern="^[1-2]\d{3}-\d{2}$"
          />
        </label>
        <button
          className={`btn btn-soft btn-success ml-4 w-40`}
          onClick={() => onCreateMonthlistBtnClick()}
          disabled={
            validatingMonthlistInput ||
            playlistExistsAlready ||
            !validMonthlistName
          }
        >
          {validatingMonthlistInput ? (
            <span className="loading loading-ring loading-xl"></span>
          ) : playlistExistsAlready === true ? (
            "exists already"
          ) : validMonthlistName ? (
            createdMonthlist ? (
              "Created!"
            ) : (
              "Create Monthlist"
            )
          ) : (
            "Invalid Monthlist"
          )}
        </button>
      </div>

      {selectedPlaylist && (
        <PlaylistModal
          playlist={selectedPlaylist}
          onClose={() => setSelectedPlaylist(null)}
        />
      )}

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
