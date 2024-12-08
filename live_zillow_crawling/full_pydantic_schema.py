import re
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import date, datetime
from openai import OpenAI
import instructor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
open_ai_key = os.getenv('open_ai_api')

# Define the Output schema (simplified placeholder, insert full schema here)
class Image(BaseModel):
    url: HttpUrl
    caption: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None

class Agent(BaseModel):
    name: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    brokerage: Optional[str] = None
    contact_link: Optional[HttpUrl] = None

class Address(BaseModel):
    street_address: Optional[str] = None
    apartment_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    neighborhood: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class InteriorFeatures(BaseModel):
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    full_bathrooms: Optional[int] = None
    flooring: Optional[List[str]] = None
    basement: Optional[str] = None
    has_fireplace: Optional[bool] = None
    heating: Optional[List[str]] = None
    cooling: Optional[List[str]] = None
    appliances: Optional[List[str]] = None
    laundry: Optional[str] = None
    total_area_sqft: Optional[int] = None
    livable_area_sqft: Optional[int] = None
    virtual_tour_link: Optional[HttpUrl] = None

class PropertyFeatures(BaseModel):
    property_type: Optional[str] = None
    subtype: Optional[List[str]] = None
    exterior_features: Optional[List[str]] = None
    patio_and_porch_features: Optional[List[str]] = None
    lot_size_sqft: Optional[int] = None
    zoning: Optional[str] = None
    parcel_number: Optional[str] = None
    year_built: Optional[int] = None
    materials: Optional[List[str]] = None
    sewer: Optional[str] = None
    water: Optional[str] = None

class CommunityFeatures(BaseModel):
    community_amenities: Optional[List[str]] = None
    hoa_fee: Optional[float] = None
    hoa_fee_frequency: Optional[str] = None
    hoa_amenities: Optional[List[str]] = None
    hoa_includes: Optional[List[str]] = None
    region: Optional[str] = None

class FinancialListingDetails(BaseModel):
    price: Optional[float] = None
    price_per_sqft: Optional[float] = None
    tax_assessed_value: Optional[float] = None
    annual_tax_amount: Optional[float] = None
    date_on_market: Optional[date] = None

class PriceHistoryEntry(BaseModel):
    event_date: Optional[date] = None
    event_type: Optional[str] = None
    price: Optional[float] = None
    price_per_sqft: Optional[float] = None
    source: Optional[str] = None

class TaxHistoryEntry(BaseModel):
    year: Optional[int] = None
    property_taxes: Optional[float] = None
    tax_assessment: Optional[float] = None

class MonthlyCostBreakdown(BaseModel):
    estimated_payment: Optional[float] = None
    principal_interest: Optional[float] = None
    mortgage_insurance: Optional[float] = None
    property_taxes: Optional[float] = None
    home_insurance: Optional[float] = None
    hoa_fees: Optional[float] = None
    utilities_included: Optional[bool] = None

class MarketValueEstimates(BaseModel):
    zestimate: Optional[float] = None
    rent_zestimate: Optional[float] = None
    estimated_sales_range_low: Optional[float] = None
    estimated_sales_range_high: Optional[float] = None

class School(BaseModel):
    name: Optional[str] = None
    grade_levels: Optional[str] = None
    distance_mi: Optional[float] = None
    rating: Optional[float] = None
    source_link: Optional[HttpUrl] = None

class AccessibilityScores(BaseModel):
    walk_score: Optional[int] = None
    transit_score: Optional[int] = None
    bike_score: Optional[int] = None

class OpenHouseEvent(BaseModel):
    date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ListingSource(BaseModel):
    listing_service: Optional[str] = None
    listing_id: Optional[str] = None
    last_checked: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class Output(BaseModel):
    address: Address
    agent: Optional[Agent] = None
    images: List[Image]
    headline_details: Optional[dict] = None
    interior: Optional[InteriorFeatures] = None
    property_details: Optional[PropertyFeatures] = None
    community: Optional[CommunityFeatures] = None
    financials: Optional[FinancialListingDetails] = None
    price_history: List[PriceHistoryEntry] = []
    tax_history: List[TaxHistoryEntry] = []
    monthly_cost: Optional[MonthlyCostBreakdown] = None
    market_value_estimates: Optional[MarketValueEstimates] = None
    schools: List[School] = []
    accessibility_scores: Optional[AccessibilityScores] = None
    open_houses: List[OpenHouseEvent] = []
    listing_source: Optional[ListingSource] = None
    special_features: Optional[List[str]] = None
    disclaimers: Optional[List[str]] = None


class ZillowParser:
    def __init__(self, model: str = "gpt-4o-mini"):
        # Initialize OpenAI and instructor client here if needed
        self.model = model
        self.client = instructor.from_openai(OpenAI(api_key=open_ai_key))

    def parse_listing(self, raw_markdown: str) -> Output:
        # Apply regex to isolate the main listing portion
        # Adjust your regex pattern as needed
        pattern = re.compile(
            r"(\$[0-9,]+\s*\n#\s*34 Golden Ave.*?)(?=## Arlington MA Real Estate & Homes For Sale|$)",
            flags=re.DOTALL
        )
        match = pattern.search(raw_markdown)
        if match:
            trimmed_text = match.group(1).strip()
        else:
            # Fallback if pattern not found
            trimmed_text = raw_markdown

        # Pass to model
        parsed_output = self.client.chat.completions.create(
            model=self.model,
            response_model=Output,
            messages=[{"role": "user", "content": trimmed_text}],
        )
        return parsed_output


# Example usage:
# If you want to do a single test run:
# parser = ZillowParser()
# result = parser.parse_listing(your_raw_markdown_here)
# print(result)
#
# If you want to keep it open as a function:
# Just call parser.parse_listing(...) whenever needed.
