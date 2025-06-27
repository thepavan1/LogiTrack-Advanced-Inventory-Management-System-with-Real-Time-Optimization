document.addEventListener("DOMContentLoaded", async function () {
  const map = L.map("map").setView([12.9716, 77.5946], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  const warehouses = {
    bangalore: { lat: 12.9716, lng: 77.5946 },
    chennai: { lat: 13.0827, lng: 80.2707 },
    hyderabad: { lat: 17.3850, lng: 78.4867 },
  };

  const vehicleIcon = L.icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/61/61231.png",
    iconSize: [40, 40],
    iconAnchor: [20, 40]
  });

  let marker = L.marker([12.9716, 77.5946], { icon: vehicleIcon }).addTo(map);
  let routeLine;

  async function animateVehicle(destination) {
    const start = marker.getLatLng();
    
    // Get the route coordinates
    const route = await getRoute(
      { lat: start.lat, lng: start.lng },
      destination
    );
    
    if (!route) {
      console.log("Using straight path as fallback");
      animateStraightPath(destination);
      return;
    }

    // Clear previous route if exists
    if (routeLine) {
      map.removeLayer(routeLine);
    }

    // Draw the new route
    routeLine = L.polyline(route, {
      color: 'blue',
      weight: 5,
      opacity: 0.7
    }).addTo(map);

    // Fit map to route bounds
    map.fitBounds(routeLine.getBounds());

    // Animate vehicle along the route
    let step = 0;
    const totalSteps = route.length;
    const animationInterval = setInterval(() => {
      if (step >= totalSteps) {
        clearInterval(animationInterval);
        alert("Vehicle reached the warehouse!");
        return;
      }
      
      marker.setLatLng(route[step]);
      map.panTo(route[step]);
      step += Math.max(1, Math.floor(totalSteps / 100)); // Adjust speed
    }, 50);
  }

  function animateStraightPath(destination) {
    // Existing straight-line animation as fallback
    let currentLatLng = marker.getLatLng();
    let steps = 100;
    let step = 0;
    let latDiff = (destination.lat - currentLatLng.lat) / steps;
    let lngDiff = (destination.lng - currentLatLng.lng) / steps;

    const interval = setInterval(() => {
      if (step >= steps) {
        clearInterval(interval);
        alert("Vehicle reached the warehouse!");
        return;
      }

      const newLat = currentLatLng.lat + latDiff * step;
      const newLng = currentLatLng.lng + lngDiff * step;
      marker.setLatLng([newLat, newLng]);
      map.panTo([newLat, newLng]);
      step++;
    }, 100);
  }

  document.getElementById("destinationSelect").addEventListener("change", function () {
    const destKey = this.value;
    animateVehicle(warehouses[destKey]);
  });
});