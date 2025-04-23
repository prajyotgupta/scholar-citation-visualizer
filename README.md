# Scholar Citation Visualizer 🌍

A Python-based tool that creates an interactive world map visualization of research citations for a specific author using Google Scholar data.

## Overview

This project fetches publication and citation data from Google Scholar for a specified author and generates an interactive world map visualization showing the global impact of their research. The visualization helps understand the geographical distribution of citations and research influence.

## Features

- Fetches publication data from Google Scholar
- Processes citation information
- Generates an interactive world map visualization
- Shows citation distribution across different countries
- Interactive tooltips with detailed information

## Prerequisites

- Python 3.7+
- Required Python packages:
  - scholarly
  - pandas
  - plotly
  - geopandas
  - pycountry

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scholar-citation-visualizer.git
cd scholar-citation-visualizer
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Update the author ID in `scholar.py`:
```python
my_author_id = 'YOUR_AUTHOR_ID'  # Replace with your Google Scholar author ID
```

2. Run the script:
```bash
python scholar.py
```

3. The script will:
   - Fetch publication data from Google Scholar
   - Process citation information
   - Generate an interactive HTML visualization

## Output

The script generates an interactive HTML file (`citation_map.html`) that can be opened in any web browser. The visualization includes:
- A world map with color-coded regions based on citation density
- Interactive tooltips showing detailed citation information
- Zoom and pan capabilities
- Country-specific citation statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [scholarly](https://github.com/scholarly-python-package/scholarly) - For Google Scholar data access
- [plotly](https://plotly.com/) - For interactive visualizations 