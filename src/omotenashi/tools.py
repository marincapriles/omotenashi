"""
Omotenashi Concierge Tools
-------------------------
This module implements the complete tool system for the Omotenashi concierge agent.
It includes both the core business logic and LangChain StructuredTool wrappers
for use with the ReAct agent.

The tools read from the property knowledge base to provide accurate, consistent
information about the luxury property's amenities, services, and offerings.
"""

from langchain.tools import StructuredTool
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field
from typing import Optional
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


class PropertyInfoInput(BaseModel):
    """No input needed for property info."""
    pass


class RecommendationInput(BaseModel):
    """Input for getting recommendations."""
    category: str = Field(
        description="Type of recommendation: dining, activities, spa, or general interest area"
    )


class ReservationInput(BaseModel):
    """Input for making reservations."""
    venue: str = Field(
        description="Restaurant or activity name, or type of venue (e.g., 'italian restaurant', 'sunset sailing')"
    )
    date_time: Optional[str] = Field(
        default="tonight",
        description="Requested date and time (e.g., 'tonight at 7pm', 'tomorrow afternoon')"
    )
    party_size: Optional[int] = Field(
        default=2,
        description="Number of guests"
    )


class SpaInput(BaseModel):
    """Input for booking spa services."""
    service: str = Field(
        description="Type of spa service or treatment desired (e.g., 'couples massage', 'signature treatment')"
    )
    preferred_time: Optional[str] = Field(
        default="tomorrow afternoon",
        description="Preferred appointment time"
    )


class CheckInOutInput(BaseModel):
    """Input for modifying check-in/out times."""
    request_type: str = Field(
        description="Type of modification: 'early check-in', 'late check-out', or general timing request"
    )
    specific_time: Optional[str] = Field(
        default=None,
        description="Specific time requested if any"
    )


# Load the property knowledge base
def load_knowledge_base():
    """Load the property knowledge base from JSON file."""
    kb_path = Path(__file__).parent.parent.parent / "data" / "property_knowledge_base.json"
    with open(kb_path, "r") as f:
        return json.load(f)

# Global knowledge base instance
KNOWLEDGE_BASE = load_knowledge_base()

# Core tool functions
def property_info() -> str:
    """Get essential property information from the knowledge base."""
    kb = KNOWLEDGE_BASE
    property_data = kb["property"]
    restaurants = kb["restaurants"]
    spa = kb["spa"]
    amenities = kb["amenities"]
    
    # Create accurate property overview from knowledge base
    dining_options = []
    for key, restaurant in restaurants.items():
        if key != "in_room_dining":
            if "rating" in restaurant:
                dining_options.append(f"{restaurant['name']} ({restaurant['rating']})")
            else:
                dining_options.append(restaurant['name'])
    
    return (
        f"{property_data['name']} - Located at {property_data['location']['address']}. "
        f"{property_data['overview']['property_size']} {property_data['location']['description']}. "
        f"Contact: {property_data['contact']['phone']} | {property_data['contact']['email']}. "
        f"Airport: {property_data['location']['airport_distance']}. "
        f"Dining: {', '.join(dining_options[:3])}. "
        f"Spa: {spa['name']} with {len(spa['facilities'])} facilities. "
        f"Amenities: {len(amenities['pools'])} pools, {amenities['beach']['type']}, fitness center"
    )

def get_recommendations(query: str) -> str:
    """Provides curated recommendations based on the guest's interests."""
    kb = KNOWLEDGE_BASE
    query_lower = query.lower()
    
    # Dining recommendations
    if any(word in query_lower for word in ["dinner", "lunch", "eat", "restaurant", "food", "dining"]):
        restaurants = kb["restaurants"]
        return f"""
        🍽️ Curated Dining Recommendations:
        
        1. **{restaurants['kaiseki']['name']}** (On property)
           - {restaurants['kaiseki']['rating']} {restaurants['kaiseki']['type']}
           - Specialty: {restaurants['kaiseki']['signature_dishes'][0]}
           - Hours: {restaurants['kaiseki']['hours']['dinner']}
           - {restaurants['kaiseki']['reservation_policy']}
        
        2. **{restaurants['il_cielo']['name']}** (On property)
           - {restaurants['il_cielo']['type']} with {restaurants['il_cielo']['special_features'][0]}
           - Famous for: {restaurants['il_cielo']['signature_dishes'][0]}
           - Hours: {restaurants['il_cielo']['hours']['dinner']}
           - Live music: {restaurants['il_cielo']['special_features'][1]}
        
        3. **{restaurants['ocean_terrace']['name']}** (On property)
           - {restaurants['ocean_terrace']['type']} with {restaurants['ocean_terrace']['special_features'][0]}
           - Today's highlight: {restaurants['ocean_terrace']['signature_dishes'][0]}
           - Hours: {restaurants['ocean_terrace']['hours']['dinner']}
        """
    
    # Spa and wellness recommendations
    elif any(word in query_lower for word in ["spa", "massage", "relax", "wellness", "treatment"]):
        spa = kb["spa"]
        signature_treatments = spa["signature_treatments"]
        return f"""
        🧘‍♀️ Wellness & Spa Recommendations:
        
        1. **{signature_treatments['omotenashi_journey']['name']}** - ${signature_treatments['omotenashi_journey']['price']}
           - Duration: {signature_treatments['omotenashi_journey']['duration']}
           - Includes: {', '.join(signature_treatments['omotenashi_journey']['includes'][:3])}
        
        2. **{signature_treatments['moonlight_ritual']['name']}** - ${signature_treatments['moonlight_ritual']['price']}
           - Duration: {signature_treatments['moonlight_ritual']['duration']}
           - Perfect for couples
        
        3. **{signature_treatments['hawaiian_healing']['name']}** - ${signature_treatments['hawaiian_healing']['price']}
           - Duration: {signature_treatments['hawaiian_healing']['duration']}
           - Traditional healing technique
        """
    
    # Activity recommendations
    elif any(word in query_lower for word in ["activity", "activities", "do", "fun", "adventure", "sport"]):
        activities = kb["activities"]
        return f"""
        🌊 Activity Recommendations:
        
        **Water Sports:**
        - {activities['water_sports'][1]['name']}: {activities['water_sports'][1]['price']}
        - {activities['water_sports'][2]['name']}: {activities['water_sports'][2]['price']} ({activities['water_sports'][2]['includes']})
        - {activities['water_sports'][0]['name']}: {activities['water_sports'][0]['price']}
        
        **Land Activities:**
        - Golf: 18-hole championship course - {activities['land_activities'][0]['rates']}
        - Tennis: {activities['land_activities'][1]['courts']} - {activities['land_activities'][1]['rates']}
        
        **Cultural Experiences:**
        - {activities['land_activities'][2]['options'][0]['name']}: {activities['land_activities'][2]['options'][0]['schedule']} - {activities['land_activities'][2]['options'][0]['price']}
        - {activities['land_activities'][2]['options'][1]['name']}: {activities['land_activities'][2]['options'][1]['schedule']} - {activities['land_activities'][2]['options'][1]['price']}
        """
    
    # General recommendations
    else:
        return """
        ✨ Personalized Recommendations:
        
        🍽️ **Dining**: Try our Michelin 2-star Kaiseki restaurant or rooftop Il Cielo for sunset views
        🧘‍♀️ **Wellness**: Indulge in our signature Omotenashi Journey spa experience
        🌊 **Activities**: Enjoy sunset sailing, championship golf, or cultural experiences
        🏖️ **Beach**: Relax on our private white sand beach with full service
        
        I'd be happy to make reservations or provide more specific recommendations based on your interests!
        """

def make_reservation(details: str) -> str:
    """Make restaurant reservations or book activities."""
    # Parse the request for context
    details_lower = details.lower()
    time_options = ["7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM"]
    selected_time = random.choice(time_options)
    
    if any(word in details_lower for word in ["italian", "il cielo", "rooftop"]):
        return f"""
        ✅ Reservation Confirmed!
        
        **Il Cielo Rooftop**
        📅 Date: Tonight
        🕰️ Time: {selected_time}
        👥 Party Size: 2 guests
        📋 Confirmation: IC-{random.randint(1000, 9999)}
        
        🌅 Perfect timing for sunset views!
        🎵 Live music tonight from 7-10 PM
        
        Please arrive 10 minutes early. We look forward to serving you!
        """
    
    elif any(word in details_lower for word in ["kaiseki", "japanese", "fine dining"]):
        return f"""
        ✅ Reservation Confirmed!
        
        **Kaiseki by Chef Yamamoto** (Michelin 2-star)
        📅 Date: Tonight
        🕰️ Time: {selected_time}
        👥 Party Size: 2 guests
        📋 Confirmation: KS-{random.randint(1000, 9999)}
        
        🍱 9-course Omakase menu included
        🍶 Sake sommelier available
        
        Smart elegant attire required. Arigato gozaimasu!
        """
    
    elif any(word in details_lower for word in ["sailing", "sunset", "boat"]):
        departure_time = "5:00 PM"
        return f"""
        ⛵ Sailing Reservation Confirmed!
        
        **Sunset Sailing Experience**
        📅 Date: Tomorrow
        🕰️ Departure: {departure_time}
        ⏱️ Duration: 2 hours
        👥 Party Size: 2 guests
        📋 Confirmation: SS-{random.randint(1000, 9999)}
        
        🥂 Includes champagne and appetizers
        🌅 Perfect for romantic sunset views
        
        Meet at the marina 15 minutes before departure!
        """
    
    else:
        return f"""
        ✅ Reservation Confirmed!
        
        **Ocean Terrace Grill**
        📅 Date: Tonight
        🕰️ Time: {selected_time}
        👥 Party Size: 2 guests
        📋 Confirmation: OT-{random.randint(1000, 9999)}
        
        🦞 Fresh seafood flown in daily
        🏖️ Beautiful beachfront dining
        
        We can accommodate any dietary preferences. See you tonight!
        """

def book_spa(service_request: str) -> str:
    """Book spa treatments and wellness services."""
    kb = KNOWLEDGE_BASE
    spa = kb["spa"]
    request_lower = service_request.lower()
    
    if any(word in request_lower for word in ["couples", "couple", "moonlight", "romantic"]):
        treatment = spa["signature_treatments"]["moonlight_ritual"]
        appointment_time = "6:00 PM"
        return f"""
        ✨ Spa Booking Confirmed!
        
        **{treatment['name']}**
        📅 Date: Tomorrow evening
        🕰️ Time: {appointment_time}
        ⏱️ Duration: {treatment['duration']}
        💰 Price: {treatment['price']}
        📋 Confirmation: MR-{random.randint(1000, 9999)}
        
        🌙 Includes: {', '.join(treatment['includes'])}
        
        Perfect for a romantic evening under the stars! Please arrive 30 minutes early for check-in.
        """
    
    elif any(word in request_lower for word in ["signature", "journey", "omotenashi"]):
        treatment = spa["signature_treatments"]["omotenashi_journey"]
        appointment_time = "10:00 AM"
        return f"""
        ✨ Spa Booking Confirmed!
        
        **{treatment['name']}**
        📅 Date: Tomorrow
        🕰️ Time: {appointment_time}
        ⏱️ Duration: {treatment['duration']}
        💰 Price: {treatment['price']}
        📋 Confirmation: OJ-{random.randint(1000, 9999)}
        
        🧘‍♀️ Includes: {', '.join(treatment['includes'])}
        
        Our most luxurious experience! Please arrive 45 minutes early to enjoy our facilities.
        """
    
    else:
        # Default massage booking
        appointment_time = "2:00 PM"
        return f"""
        ✨ Spa Booking Confirmed!
        
        **Relaxation Massage**
        📅 Date: Tomorrow
        🕰️ Time: {appointment_time}
        ⏱️ Duration: 90 minutes
        💰 Price: $285
        📋 Confirmation: RM-{random.randint(1000, 9999)}
        
        🌿 Includes aromatherapy and hot stone elements
        ♨️ Complimentary onsen access before treatment
        
        Please arrive 30 minutes early for consultation. We look forward to pampering you!
        """

def modify_checkin_checkout(request: str) -> str:
    """Arrange flexible check-in and check-out times."""
    kb = KNOWLEDGE_BASE
    policies = kb["policies"]["check_in_out"]
    request_lower = request.lower()
    
    if any(word in request_lower for word in ["early", "check-in", "checkin"]):
        return f"""
        ✅ Early Check-in Arranged!
        
        **Standard Check-in**: {policies['standard_check_in']}
        **Your Early Check-in**: 1:00 PM
        
        📋 Confirmation: ECI-{random.randint(1000, 9999)}
        
        🏨 Room will be ready by 1:00 PM tomorrow
        🧳 Complimentary luggage storage available if you arrive earlier
        ☕ Welcome refreshments in the lobby
        
        {policies['early_check_in']}
        We're delighted to accommodate your travel schedule!
        """
    
    elif any(word in request_lower for word in ["late", "check-out", "checkout"]):
        return f"""
        ✅ Late Check-out Approved!
        
        **Standard Check-out**: {policies['standard_check_out']}
        **Your Late Check-out**: 4:00 PM
        
        📋 Confirmation: LCO-{random.randint(1000, 9999)}
        
        🛏️ Room available until 4:00 PM
        🧳 Extended luggage storage if needed
        🍽️ Late lunch available via room service
        
        {policies['late_check_out']}
        Enjoy your extra time with us!
        """
    
    else:
        return f"""
        ✅ Flexible Timing Arranged!
        
        We're happy to accommodate your schedule:
        
        **Check-in Options:**
        • Standard: {policies['standard_check_in']}
        • Early check-in available: {policies['early_check_in']}
        
        **Check-out Options:**
        • Standard: {policies['standard_check_out']}
        • Late check-out available: {policies['late_check_out']}
        
        📞 Please call concierge at arrival to confirm your preferred times
        🎯 We'll ensure everything is perfectly timed for your convenience!
        """

# Tool wrapper functions that match expected signatures
def property_info_wrapper(dummy: str = "") -> str:
    """Wrapper for property_info that accepts the required input."""
    return property_info()

def get_recommendations_wrapper(category: str) -> str:
    """Wrapper for get_recommendations with structured input."""
    return get_recommendations(category)

def make_reservation_wrapper(venue: str, date_time: str = "tonight", party_size: int = 2) -> str:
    """Wrapper for make_reservation with structured input."""
    details = f"{venue} for {party_size} people {date_time}"
    return make_reservation(details)

def book_spa_wrapper(service: str, preferred_time: str = "tomorrow afternoon") -> str:
    """Wrapper for book_spa with structured input."""
    request = f"{service} {preferred_time}"
    return book_spa(request)

def modify_checkin_checkout_wrapper(request_type: str, specific_time: Optional[str] = None) -> str:
    """Wrapper for modify_checkin_checkout with structured input."""
    request = request_type
    if specific_time:
        request += f" at {specific_time}"
    return modify_checkin_checkout(request)


# Create LangChain StructuredTools
property_info_tool = StructuredTool.from_function(
    func=property_info_wrapper,
    name="property_info",
    description="Get comprehensive information about the luxury property including amenities, dining options, facilities, and services. Use this when guests ask about the hotel or resort.",
    args_schema=PropertyInfoInput,
    return_direct=False
)

recommendations_tool = StructuredTool.from_function(
    func=get_recommendations_wrapper,
    name="get_recommendations",
    description="Get curated, personalized recommendations for dining, activities, spa experiences, or other interests. Always use this to exceed guest expectations by providing comprehensive options.",
    args_schema=RecommendationInput,
    return_direct=False
)

reservation_tool = StructuredTool.from_function(
    func=make_reservation_wrapper,
    name="make_reservation",
    description="Make restaurant reservations or book activities and experiences. Provides immediate confirmation with all details.",
    args_schema=ReservationInput,
    return_direct=False
)

spa_tool = StructuredTool.from_function(
    func=book_spa_wrapper,
    name="book_spa",
    description="Book spa treatments and wellness services. Offers the signature Omotenashi Journey and other luxury treatments.",
    args_schema=SpaInput,
    return_direct=False
)

checkin_checkout_tool = StructuredTool.from_function(
    func=modify_checkin_checkout_wrapper,
    name="modify_checkin_checkout",
    description="Arrange flexible check-in and check-out times to accommodate guest schedules. Provides early check-in, late check-out, and customized timing options.",
    args_schema=CheckInOutInput,
    return_direct=False
)


# Export all tools as a list
ALL_TOOLS = [
    property_info_tool,
    recommendations_tool,
    reservation_tool,
    spa_tool,
    checkin_checkout_tool
]


# Tool name mapping for easy reference
TOOL_MAP = {
    "property_info": property_info_tool,
    "get_recommendations": recommendations_tool,
    "make_reservation": reservation_tool,
    "book_spa": spa_tool,
    "modify_checkin_checkout": checkin_checkout_tool
}


if __name__ == "__main__":
    """Test the LangChain tools independently."""
    print("Testing LangChain Tools\n" + "="*50)
    
    # Test property info
    print("\n1. Property Info Tool:")
    result = property_info_tool.run({})
    print(result)
    
    # Test recommendations
    print("\n2. Recommendations Tool:")
    result = recommendations_tool.run({"category": "dining"})
    print(result)
    
    # Test reservation
    print("\n3. Reservation Tool:")
    result = reservation_tool.run({
        "venue": "italian restaurant",
        "date_time": "tonight at 8pm",
        "party_size": 4
    })
    print(result)