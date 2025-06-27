// routing.js - Using OSRM (Open Source Routing Machine)

async function getRoute(start, end) {
  try {
    // Using OSRM demo server (replace with your own instance if needed)
    const response = await fetch(
      `https://router.project-osrm.org/route/v1/driving/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full&geometries=geojson`
    );
    const data = await response.json();
    
    if (data.routes && data.routes.length > 0) {
      // Convert GeoJSON coordinates to [lat, lng] format
      return data.routes[0].geometry.coordinates.map(coord => [coord[1], coord[0]]);
    }
    throw new Error("No route found");
  } catch (error) {
    console.error("Error fetching route:", error);
    return null;
  }
}