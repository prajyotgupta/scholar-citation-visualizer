# Scholar Citation Visualizer

A Python tool that visualizes the geographical distribution of citations for a Google Scholar author. This tool fetches author details, their publications, and citations, then creates a world map showing where the citing authors are located.

## Features

- Fetches author details and publications from Google Scholar
- Analyzes citations and their authors
- Geocodes author affiliations to their geographical locations
- Creates an interactive world map visualization
- Handles various affiliation formats and common institutions

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Update the `AUTHOR_ID` in `scholar.py` with your Google Scholar ID
2. Run the script:
```bash
python scholar.py
```

The script will:
- Fetch author details and publications
- Process citations
- Create a map visualization
- Save the map as `citations_map.png`

## Visualization

The tool creates a world map showing the geographical distribution of citing authors. Each point on the map represents an institution where citing authors are affiliated.

![Citation Map](citations_map.png)

## Dependencies

- scholarly
- geopy
- plotly
- kaleido
- certifi

## License

MIT License 