from scholarly import scholarly
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
import plotly.io
import ssl
import certifi
import time
import re

# Google Scholar Author ID
# https://scholar.google.com/citations?user=FA9h3ngAAAAJ&hl=en
AUTHOR_ID = 'FA9h3ngAAAAJ'

# Common location mappings
LOCATION_MAPPINGS = {
    'UCLA': 'Los Angeles, California, USA',
    'Loyola University Chicago': 'Chicago, Illinois, USA',
    'Washington State University': 'Pullman, Washington, USA',
    'Harbin Institute of Technology': 'Harbin, China',
    'University of Wisconsin-Madison': 'Madison, Wisconsin, USA',
    'Tsinghua University': 'Beijing, China',
    'Stanford University': 'Stanford, California, USA',
    'New Mexico State University': 'Las Cruces, New Mexico, USA',
    'WorldServe Education': 'Bangalore, India',
    'COMSATS University': 'Islamabad, Pakistan',
    'Macquarie University': 'Sydney, Australia',
    'Lancaster University': 'Lancaster, UK',
    'University of Houston': 'Houston, Texas, USA',
    'University of Science and Technology of China': 'Hefei, China',
    'Beijing Jiaotong University': 'Beijing, China',
    'National Institute of Technology Hamirpur': 'Hamirpur, India',
    'VNR VJIET': 'Hyderabad, India',
    'SNS College of Technology': 'Coimbatore, India',
    'Intel Corporation': 'Santa Clara, California, USA',
}

def clean_affiliation(affiliation):
    """Clean affiliation string to extract institution name"""
    # Remove common prefixes
    prefixes = ['Assistant Professor', 'Professor', 'PhD Student', 'Ph.D. Candidate', 
                'Research Assistant', 'Managing Director', 'Engineer', 'Doctor of Philosophy',
                'Associate Professor', 'Senior Design Engineer']
    
    for prefix in prefixes:
        if affiliation.startswith(prefix):
            affiliation = affiliation[len(prefix):].strip()
            if affiliation.startswith(','):
                affiliation = affiliation[1:].strip()
            if affiliation.startswith('at'):
                affiliation = affiliation[2:].strip()
    
    # Remove anything in brackets
    affiliation = re.sub(r'\([^)]*\)', '', affiliation)
    affiliation = re.sub(r'\[[^\]]*\]', '', affiliation)
    
    # Remove specific phrases
    affiliation = affiliation.replace('Formerly HOD, Dean(R&C), Dean Acad', '')
    affiliation = affiliation.replace('IEEE Fellow, AAIA Fellow, ACM Distinguished Member', '')
    
    return affiliation.strip()

def get_geocoder():
    """Create and return a configured geocoder with SSL context"""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return Nominatim(user_agent="my_geocoder", ssl_context=ssl_context, timeout=10)

def geocode_location(geolocator, location):
    """Safely geocode a location with retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            location_info = geolocator.geocode(location)
            if location_info:
                return location_info.latitude, location_info.longitude, location_info.address
            time.sleep(1)  # Wait before retrying
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {location}: {e}")
            time.sleep(2)  # Wait longer between retries
    return None, None, None

def print_author_details(author):
    """
    Print author details in a readable format.
    """
    print("\n" + "="*50)
    print("AUTHOR DETAILS")
    print("="*50)
    print(f"Name: {author.get('name', 'N/A')}")
    print(f"Affiliation: {author.get('affiliation', 'N/A')}")
    print(f"Interests: {', '.join(author.get('interests', ['N/A']))}")
    print(f"Citations: {author.get('citedby', 0):,}")
    print(f"h-index: {author.get('hindex', 0)}")
    print(f"i10-index: {author.get('i10index', 0)}")
    
    if 'publications' in author:
        print("\n" + "-"*50)
        print("RECENT PUBLICATIONS")
        print("-"*50)
        for i, pub in enumerate(author['publications'][:5], 1):
            print(f"\n{i}. {pub.get('bib', {}).get('title', 'N/A')}")
            print(f"   Year: {pub.get('bib', {}).get('pub_year', 'N/A')}")
            print(f"   Citations: {pub.get('num_citations', 0)}")
            print(f"   Authors: {pub.get('bib', {}).get('author', 'N/A')}")

def scholar_visualizer():
    """
    This function searches for an author's details and publications using the scholarly library.
    Modified to process only a specific paper.
    """
    # Add your author ID here
    my_author_id = AUTHOR_ID
    
    # Specific paper citation ID from the URL
    target_citation_id = "u-x6o8ySG0sC"  # Updated citation ID for the new paper

    # Search for author
    author = scholarly.search_author_id(my_author_id)

    # Fill author details
    scholarly.fill(author, sections=['publications'])
    
    # Print formatted author details
    print_author_details(author)

    # Find the specific publication
    target_publication = None
    for pub in author['publications']:
        # The citation ID is typically in the 'author_pub_id' field
        if pub.get('author_pub_id', '').endswith(target_citation_id):
            target_publication = pub
            break
    
    if not target_publication:
        print(f"Could not find publication with citation ID: {target_citation_id}")
        return
    
    print(f"\n" + "="*50)
    print("TARGET PUBLICATION FOUND")
    print("="*50)
    print(f"Title: {target_publication.get('bib', {}).get('title', 'N/A')}")
    print(f"Year: {target_publication.get('bib', {}).get('pub_year', 'N/A')}")
    print(f"Citations: {target_publication.get('num_citations', 0)}")
    print(f"Authors: {target_publication.get('bib', {}).get('author', 'N/A')}")

    # Get citations for this specific publication only
    all_citations = []
    try:
        citations = scholarly.citedby(target_publication)
        all_citations.extend(citations)
        print(f"\nSuccessfully retrieved {len(all_citations)} citations for this paper")
    except KeyError:
        print(f"KeyError encountered for publication: {target_publication}. Skipping.")
        return

    print(f"Total citations for this paper: {len(all_citations)}")

    # Process cited authors
    cited_authors = []
    for c in all_citations:
        print(f"Processing citation: {c['bib']['title']}")
        try:
            for a_id in c['author_id']:
                if a_id:
                    a = scholarly.search_author_id(a_id)
                    if a:
                        cited_authors.append(a)
                        print(f"\t{a['name']}|{a['affiliation']}")
        except KeyError:
            print(f"KeyError encountered for citation: {c}. Skipping.")

    # Get unique affiliations
    affiliations = set()
    for a in cited_authors:
        if 'affiliation' in a:
            affiliations.add(a['affiliation'])

    # Print affiliations
    print("\n" + "="*50)
    print("AFFILIATIONS FOUND")
    print("="*50)
    for aff in affiliations:
        print(aff)

    # Analyze citations with missing author info
    empty_author_citations = []
    authors_with_no_ids = {}  # title -> authors
    for c in all_citations:
        non_empty_count = 0
        no_ids = []
        for i, a_id in enumerate(c['author_id']):
            if a_id:
                non_empty_count += 1
            else:
                no_ids.append(c['bib']['author'][i])
        if no_ids:
            authors_with_no_ids[c['bib']['title']] = no_ids
        if non_empty_count == 0:
            empty_author_citations.append(c)
            print(f"Empty author info for citation: {c['bib']['title']}")

    print(f"Citations with empty author info: {len(empty_author_citations)}")
    for k, v in authors_with_no_ids.items():
        print(k, v)
    print(f"Authors with no ids: {len(authors_with_no_ids)}")

    # Geocode locations and create map
    geolocator = get_geocoder()
    latitudes = []
    longitudes = []
    location_names = []
    addresses = []

    print("\n" + "="*50)
    print("GEOCODING RESULTS")
    print("="*50)

    for affiliation in affiliations:
        # First try to find a direct mapping
        cleaned_aff = clean_affiliation(affiliation)
        location_to_geocode = None
        
        # Check if any of the mapped institutions are in the affiliation
        for institution, location in LOCATION_MAPPINGS.items():
            if institution.lower() in cleaned_aff.lower():
                location_to_geocode = location
                print(f"Using mapped location for {institution}: {location}")
                break
        
        # If no mapping found, use the cleaned affiliation
        if not location_to_geocode:
            location_to_geocode = cleaned_aff

        lat, lon, address = geocode_location(geolocator, location_to_geocode)
        
        if lat is not None and lon is not None:
            latitudes.append(lat)
            longitudes.append(lon)
            location_names.append(affiliation)
            addresses.append(address)
            print(f"✓ Successfully geocoded: {affiliation} -> {address}")
        else:
            print(f"✗ Could not geocode: {affiliation} -> {location_to_geocode}")

    if latitudes and longitudes:
        # Create and save the map
        fig = go.Figure(data=go.Scattergeo(
            lon=longitudes,
            lat=latitudes,
            text=location_names,
            mode='markers',
            marker_color="blue"
        ))
        
        fig.update_geos(
            visible=True,
            scope="world",
            showcountries=True,
            countrycolor="Grey"
        )
        
        fig.update_layout(
            title=f'Citations Map for: {target_publication.get("bib", {}).get("title", "Target Paper")}',
            geo_scope='world',
        )
        
        # Save the figure
        fig.write_image("citations_map_single_paper.png", scale=2)
        print("\nMap saved as citations_map_single_paper.png")
        print(f"Total locations mapped: {len(latitudes)}")
        
        # Print summary of locations
        print("\n" + "="*50)
        print("SUMMARY OF LOCATIONS")
        print("="*50)
        for i, (affiliation, address) in enumerate(zip(location_names, addresses), 1):
            print(f"{i}. {affiliation}")
            print(f"   -> {address}")
            print()
        
    else:
        print("\nNo valid locations found to create map")
    
    # Print the hierarchical citation tree
    print_citation_tree(target_publication, all_citations, cited_authors)

def print_citation_tree(target_publication, all_citations, cited_authors):
    """
    Print a hierarchical tree structure showing the paper, citing papers, and affiliations.
    Better organized to match authors with their specific citing papers.
    """
    print("\n" + "="*80)
    print("CITATION TREE")
    print("="*80)
    
    # Main paper
    target_title = target_publication.get('bib', {}).get('title', 'Target Paper')
    print(f"📄 {target_title}")
    
    # Create a mapping of author names to affiliations from our cited_authors
    author_affiliation_map = {}
    for author in cited_authors:
        if 'name' in author and 'affiliation' in author:
            author_affiliation_map[author['name']] = author['affiliation']
    
    # Process each citation and its authors
    for i, citation in enumerate(all_citations, 1):
        citation_title = citation['bib']['title']
        print(f"│")
        if i == len(all_citations):  # Last citation
            print(f"└── 📝 {citation_title}")
            connector = "    "
        else:
            print(f"├── 📝 {citation_title}")
            connector = "│   "
        
        # Get authors from the citation
        citation_has_authors = False
        authors = []
        
        # Try to get author names from the bib data
        if 'author' in citation.get('bib', {}):
            bib_authors = citation['bib']['author']
            if isinstance(bib_authors, str):
                # Single author or comma-separated string
                if ',' in bib_authors and ' and ' not in bib_authors:
                    authors = [name.strip() for name in bib_authors.split(',')]
                else:
                    authors = [bib_authors]
            elif isinstance(bib_authors, list):
                authors = bib_authors
        
        # If we have authors, display them with affiliations
        if authors:
            for j, author_name in enumerate(authors):
                is_last_author = (j == len(authors) - 1)
                
                # Clean up author name (remove extra spaces, etc.)
                clean_author = author_name.strip()
                
                # Check if we have affiliation info for this author
                affiliation_found = None
                for known_name, affiliation in author_affiliation_map.items():
                    # Try different matching strategies
                    if (clean_author.lower() == known_name.lower() or 
                        clean_author.lower() in known_name.lower() or
                        known_name.lower() in clean_author.lower()):
                        affiliation_found = affiliation
                        break
                
                # Format the output
                if is_last_author:
                    branch = "└──"
                else:
                    branch = "├──"
                
                if affiliation_found:
                    print(f"{connector}{branch} 🏛️  {clean_author} → {affiliation_found}")
                else:
                    print(f"{connector}{branch} 👤 {clean_author} (No institutional information)")
                
                citation_has_authors = True
        
        # If we still don't have authors, check if any of our known authors might be from this paper
        if not citation_has_authors:
            # Check if any cited authors might be associated with this citation title
            found_match = False
            for author in cited_authors:
                if 'name' in author:
                    # This is a very basic heuristic - in reality, this would need more sophisticated matching
                    print(f"{connector}└── ❓ No author information available")
                    found_match = True
                    break
            
            if not found_match:
                print(f"{connector}└── ❓ No author information available")
    
    print(f"│")
    print("└── End of citations")

if __name__ == "__main__":
    scholar_visualizer()