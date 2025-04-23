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
    """
    # Add your author ID here
    my_author_id = AUTHOR_ID

    # Search for author
    author = scholarly.search_author_id(my_author_id)

    # Fill author details
    scholarly.fill(author, sections=['publications'])
    
    # Print formatted author details
    print_author_details(author)

    # Get all citations
    all_citations = []
    for pub in author['publications']:
        try:
            citations = scholarly.citedby(pub)
            all_citations.extend(citations)
        except KeyError:
            print(f"KeyError encountered for publication: {pub}. Skipping.")

    print(f"Total citations: {len(all_citations)}")

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
            title='Citations Map',
            geo_scope='world',
        )
        
        # Save the figure
        fig.write_image("citations_map.png", scale=2)
        print("\nMap saved as citations_map.png")
        print(f"Total locations mapped: {len(latitudes)}")
    else:
        print("\nNo valid locations found to create map")

if __name__ == "__main__":
    scholar_visualizer()