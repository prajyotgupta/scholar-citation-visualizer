from scholarly import scholarly

# Google Scholar Author ID
# https://scholar.google.com/citations?user=FA9h3ngAAAAJ&hl=en
AUTHOR_ID = 'FA9h3ngAAAAJ'

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

if __name__ == "__main__":
    scholar_visualizer()