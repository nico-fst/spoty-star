export interface Playlist {
    description: string;
    href: string;
    id: string;
    images: { height: number, url: string, width: number }[]; // Array weil verschiedene Größen
    name: string;
    tracks: { href: string; total: string };
    uri: string;
}