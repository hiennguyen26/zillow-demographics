import json
import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from pathlib import Path
import re
from full_pydantic_schema import ZillowParser

# Load environment variables
load_dotenv()
firecrawl_api_key = os.getenv('firecrawl_api_key')
crawler = FirecrawlApp(api_key=firecrawl_api_key)

def extract_sections(markdown_content):
    # Find all headings (# through ######)
    heading_pattern = r'^(#{1,6})\s+(.+?)$'
    headings = re.finditer(heading_pattern, markdown_content, re.MULTILINE)
    
    # Define sections to keep
    sections_to_keep = {
        "What's special", "Travel times", "Facts & features", "Interior",
        "Bedrooms & bathrooms", "Heating", "Cooling", "Features", "Interior area",
        "Property", "Parking", "Lot", "Details", "Construction", "Type & style",
        "Materials", "Condition", "Utilities & green energy", "Community & HOA",
        "HOA", "Location", "Financial & listing details", "Estimated market value",
        "Price history", "Public tax history", "Monthly payment", "Property taxes",
        "Home insurance", "HOA fees", "Climate risks", "Getting around",
        "Nearby schools", "GreatSchools rating"
    }
    
    # Create ordered list of headings with their levels and positions
    sections = []
    positions = []
    
    # Store all headings first to properly handle section boundaries
    all_headings = list(headings)
    for i, match in enumerate(all_headings):
        level = len(match.group(1))
        title = match.group(2).strip()
        
        if title in sections_to_keep:
            sections.append({
                'level': level,
                'title': title,
                'position': match.start(),
                'next_position': all_headings[i + 1].start() if i + 1 < len(all_headings) else len(markdown_content)
            })
    
    # Extract content between kept sections
    filtered_content = ""
    for section in sections:
        # Get the heading line
        heading = '#' * section['level'] + ' ' + section['title'] + '\n\n'
        # Get content until next section
        content = markdown_content[section['position']:section['next_position']].strip()
        # Remove the heading from content since we're adding it separately
        content = content[content.find('\n'):].strip()
        filtered_content += heading + content + '\n\n'

    return sections, filtered_content

def process_zillow_properties():
    # Load JSON file
    json_path = r"C:\Coding\Github Repos\zillow-demographics\zillow-demographics\data\Properties_boston_zillow_dec8_400.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Create output directories if they don't exist
    output_dir_markdown = Path("output/markdown_files")
    output_dir_json = Path("output/json_files")
    output_dir_markdown.mkdir(parents=True, exist_ok=True)
    output_dir_json.mkdir(parents=True, exist_ok=True)
    
    # Initialize parser
    parser = ZillowParser()
    
    # Process first property only
    item = data[4]
    zillow_url = item['property_url']
    property_id_address = item['address']
    
    # Create output filenames
    safe_filename = "".join(x for x in property_id_address if x.isalnum() or x in (' ', '-', '_'))
    markdown_path = output_dir_markdown / f"{safe_filename}.md"
    json_path = output_dir_json / f"{safe_filename}.json"
    
    try:
        response = crawler.scrape_url(
            url=zillow_url,
            params={
                'formats': ['markdown']
            }
        )
        
        # Extract sections and filtered content
        sections, filtered_content = extract_sections(response['content'])
        
        # Print sections for analysis
        print("\nHeadings found (in order):")
        for section in sections:
            print(f"{'#' * section['level']} {section['title']}")
            
        # Save filtered markdown
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(filtered_content)
            
        # Parse filtered content to structured data
        parsed_data = parser.parse_listing(filtered_content)
        
        # Save structured JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            # Convert Pydantic model to JSON
            json.dump(parsed_data.model_dump(exclude_none=True), f, indent=2, default=str)
            
        print(f"\nSuccessfully processed {zillow_url}")
        print(f"Markdown saved to: {markdown_path}")
        print(f"JSON saved to: {json_path}")
        
    except Exception as e:
        print(f"Error processing {zillow_url}: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    process_zillow_properties()