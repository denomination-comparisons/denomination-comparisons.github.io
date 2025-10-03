# AKK-CH5 Transcript Archive

This repository contains **40 raw transcripts** from Kathryn Krick's YouTube ministry materials, organized into three playlists.

## Structure
- **new-believer/** — 23 episodes
- **receiving-and-maintaining-your-deliverance/** — 6 episodes
- **revival-is-now-podcast/** — 11 episodes

## Index
For a visual index with links, see [index.html](index.html).

## AI Parsing Best Practices
### For ChatGPT
- If HTML parsing fails, read `manifest.json` for full playlist/episode data.
- Backup direct YouTube links are stored in `manifest.json`.

### For Claude
- Use `manifest.json` when HTML load is slow due to crawl-lag.

### For Grok
- Structured `.html` and `.json` files included to allow direct parsing without `.txt` format quirks.

## Fallback
- All local `.txt` files are stored in subfolders by playlist.
- `manifest.json` contains playlist, episode number, title, and placeholder YouTube links.

## Example Local File Path
