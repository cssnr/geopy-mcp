import asyncio
import logging
from typing import Annotated, Any

from geopy.distance import geodesic  # type: ignore[import-untyped]
from geopy.geocoders import Nominatim  # type: ignore[import-untyped]
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field

from ._version import __version__

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "geopy",
    json_response=True,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

# noinspection PyProtectedMember
mcp._mcp_server.version = __version__

logger.info("geopy-mcp: %s", __version__)

geolocator = Nominatim(user_agent=f"geopy-mcp/{__version__}")


@mcp.tool()
async def geocode(
    address: Annotated[str, Field(description="Address or location name")],
    limit: Annotated[int, Field(ge=1, le=10, description="Max results (1-10)")] = 1,
) -> list[dict[str, Any]]:
    """Convert an address to latitude/longitude coordinates."""
    results = await asyncio.to_thread(geolocator.geocode, address, exactly_one=False, limit=limit)
    logger.info("results: %s", results)
    if not results:
        return []
    return [
        {
            "address": r.address,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "name": r.raw.get("name"),
            # "raw": r.raw,
        }
        for r in results
    ]


@mcp.tool()
async def reverse_geocode(
    latitude: Annotated[float, Field(ge=-90, le=90, description="Latitude (-90 to 90)")],
    longitude: Annotated[float, Field(ge=-180, le=180, description="Longitude (-180 to 180)")],
) -> dict[str, Any] | None:
    """Convert coordinates to an address (full address, lat/lng, name)."""
    location = await asyncio.to_thread(geolocator.reverse, f"{latitude}, {longitude}")
    logger.info("location: %s", location)
    if not location:
        return None
    return {
        "address": location.address,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "name": location.raw.get("name"),
        # "raw": location.raw,
    }


@mcp.tool()
async def calculate_distance(
    latitude1: Annotated[float, Field(ge=-90, le=90, description="Latitude of first location")],
    longitude1: Annotated[float, Field(ge=-180, le=180, description="Longitude of first location")],
    latitude2: Annotated[float, Field(ge=-90, le=90, description="Latitude of second location")],
    longitude2: Annotated[float, Field(ge=-180, le=180, description="Longitude of second location")],
) -> dict[str, Any]:
    """Calculate distance between two coordinates. Returns km, miles, meters, feet, nautical_miles."""
    distance = geodesic((latitude1, longitude1), (latitude2, longitude2))
    logger.info("distance: %s", distance)
    return {
        "from": {
            "latitude": latitude1,
            "longitude": longitude1,
        },
        "to": {
            "latitude": latitude2,
            "longitude": longitude2,
        },
        "distance": {
            "kilometers": distance.km,
            "miles": distance.miles,
            "meters": distance.meters,
            "feet": distance.feet,
            "nautical_miles": distance.nautical,
        },
    }


@mcp.tool()
async def distance_between_places(
    place1: Annotated[str, Field(description="First address or location name")],
    place2: Annotated[str, Field(description="Second address or location name")],
) -> dict[str, Any]:
    """Calculate distance between two addresses. Geocodes both, returns address+coords+distances (km, miles, meters, feet, nautical_miles)."""
    from_loc = await asyncio.to_thread(geolocator.geocode, place1)
    if not from_loc:
        return {"error": f"Could not geocode place1: {place1}"}
    to_loc = await asyncio.to_thread(geolocator.geocode, place2)
    if not to_loc:
        return {"error": f"Could not geocode place2: {place2}"}
    distance = geodesic((from_loc.latitude, from_loc.longitude), (to_loc.latitude, to_loc.longitude))
    logger.info("distance: %s", distance)
    return {
        "from": {
            "query": place1,
            "address": from_loc.address,
            "latitude": from_loc.latitude,
            "longitude": from_loc.longitude,
        },
        "to": {
            "query": place2,
            "address": to_loc.address,
            "latitude": to_loc.latitude,
            "longitude": to_loc.longitude,
        },
        "distance": {
            "kilometers": distance.km,
            "miles": distance.miles,
            "meters": distance.meters,
            "feet": distance.feet,
            "nautical_miles": distance.nautical,
        },
    }


def main():
    mcp.run(transport="stdio")


app = mcp.streamable_http_app()
