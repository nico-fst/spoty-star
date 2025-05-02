import React, { useState } from "react";

interface SearchOptionedProps {
  options: string[];
  buttonTitle: string;
}

const SearchOptioned = ({ options, buttonTitle }: SearchOptionedProps) => {
  const [search, setSearch] = useState<string>("");

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const filteredOptions = options.filter((option) =>
    option.toLowerCase().includes(search.toLowerCase())
  );

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
        <input type="search" className="grow" placeholder="Search" value={search} onChange={handleSearchChange}/>
      </label>

      <ul className="list bg-base-100 rounded-box shadow-md">
        <br></br>
        {/* <li className="p-4 pb-2 text-xs opacity-60 tracking-wide">
          Search results
        </li> */}
        {filteredOptions.map((option, index) => {
          return (
            <>
              <li className="list-row">
                <div className="text-4xl font-thin opacity-30 tabular-nums">
                  {index + 1}
                </div>
                <div>
                  <img
                    className="size-10 rounded-box"
                    src="https://img.daisyui.com/images/profile/demo/1@94.webp"
                  />
                </div>
                <div className="list-col-grow flex items-center">
                  <div>{option}</div>
                </div>
                <button className="btn btn-secondary">{buttonTitle}</button>
              </li>
            </>
          );
        })}
      </ul>
    </>
  );
};

export default SearchOptioned;
