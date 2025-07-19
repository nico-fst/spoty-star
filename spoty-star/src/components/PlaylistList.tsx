import { Playlist } from "../types";

interface PlaylistListProps {
  playlists: Playlist[];
  search: string;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  setSelectedPlaylist: (pl: Playlist) => void;
  fetchingPlaylists: boolean;
}

export const PlaylistList = ({
  playlists,
  search,
  currentPage,
  setCurrentPage,
  fetchingPlaylists,
  setSelectedPlaylist,
}: PlaylistListProps) => {
  const ITEMS_PER_PAGE = 25;

  const filteredOptions = playlists
    .filter((option) =>
      option.name.toLowerCase().includes(search.toLowerCase()),
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  const pageCount = Math.ceil(filteredOptions.length / ITEMS_PER_PAGE);

  return (
    <>
      {playlists.length > 0 && !fetchingPlaylists ? (
        <>
          <ul className="list bg-base-100 rounded-box shadow-md">
            <li className="p-4 pb-2 text-xs opacity-60 tracking-wide mt-4">
              {filteredOptions.length > 99 ? "99+" : filteredOptions.length}{" "}
              {filteredOptions.length === 1 ? "result" : "results"}
            </li>
            {/* Playlists for current page */}
            {filteredOptions
              .slice(
                (currentPage - 1) * ITEMS_PER_PAGE,
                currentPage * ITEMS_PER_PAGE,
              )
              .map((pl) => {
                const globalIndex = filteredOptions.indexOf(pl); // Index von playlist in gesamter Liste

                return (
                  <>
                    <li className="list-row">
                      <div className="text-4xl font-thin opacity-10 tabular-nums w-20 text-right pr-4">
                        {globalIndex + 1}
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

          {/* Pagination - only if more than ITEMS_PER_PAGE options */}
          {pageCount > 1 && (
            <div className="join flex justify-center w-full mt-8">
              {[...Array(pageCount)].map((_, i) => (
                <button
                  key={i}
                  className="join-item btn"
                  onClick={() => {
                    setCurrentPage(i + 1);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          )}
        </>
      ) : (
        // Skeleton when loading === fetchingPlaylists
        <ul className="list bg-base-100 rounded-box shadow-md">
          <li className="p-4 pb-2 text-xs opacity-60 tracking-wide mt-4">
            loading...
          </li>
          {[...Array(ITEMS_PER_PAGE)].map((_, index) => {
            return (
              <>
                <li className="list-row">
                  <div className="text-4xl font-thin opacity-10 tabular-nums w-20 text-right pr-4">
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
    </>
  );
};
