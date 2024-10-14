# spoty-star
A Spotify Flask Server automating spotify workflows

# Debugging Nightmares

- localhost bei redirect und /callback nicht gleich behandelt wie 127.0.0.1
- it seems that tracks of a given playlist can only be fetched in chunks of 100 (since there is no skip_duplicate param when adding to playlists...)