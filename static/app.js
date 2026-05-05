// Global App Logic
console.log("app.js loaded once at", new Date().toISOString());

document.addEventListener('DOMContentLoaded', () => {
    // 1. Splash Screen Logic
    const splashScreen = document.getElementById('splash-screen');
    if (splashScreen) {
        // Hide splash screen after 2.5 seconds
        setTimeout(() => {
            splashScreen.style.opacity = '0';
            setTimeout(() => {
                splashScreen.style.display = 'none';
            }, 500); // Wait for transition
        }, 2500);
    }

    // 2. Button Ripple Effect
    const buttons = document.querySelectorAll('.btn-ripple');
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;
            
            const ripples = document.createElement('span');
            ripples.style.left = x + 'px';
            ripples.style.top = y + 'px';
            ripples.classList.add('ripple');
            
            this.appendChild(ripples);
            
            setTimeout(() => {
                ripples.remove();
            }, 600);
        });
    });

    // 3. SOS Button Long Press & Pulse
    const sosBtn = document.getElementById('sos-trigger');
    if (sosBtn) {
        console.log("SOS button found in DOM");
        let pressTimer;
        
        sosBtn.addEventListener('mousedown', () => {
            sosBtn.style.transform = 'scale(0.9)';
            pressTimer = window.setTimeout(() => {
                triggerSOS();
            }, 1500); // 1.5 seconds long press
        });
        
        sosBtn.addEventListener('mouseup', () => {
            clearTimeout(pressTimer);
            sosBtn.style.transform = 'scale(1)';
        });
        
        sosBtn.addEventListener('mouseleave', () => {
            clearTimeout(pressTimer);
            sosBtn.style.transform = 'scale(1)';
        });
        
        // Touch events for mobile
        sosBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            sosBtn.style.transform = 'scale(0.9)';
            pressTimer = window.setTimeout(() => {
                triggerSOS();
            }, 1500);
        });
        
        sosBtn.addEventListener('touchend', () => {
            clearTimeout(pressTimer);
            sosBtn.style.transform = 'scale(1)';
        });
    }

    // 4. Initialize SOS WebSocket if authenticated
    const isAuthenticated = document.body.dataset.authenticated === 'true';
    if (isAuthenticated) {
        connectSOSSocket();
    }
});

// Robust Retry-Based Loader for SOS Marker
function waitForMapAndShowSOS() {
    const pending = sessionStorage.getItem("pendingSOSLocation");
    if (!pending) return;

    try {
        const sosData = JSON.parse(pending);
        let attempts = 0;

        const interval = setInterval(() => {
            if (window.map && typeof window.showSOSMarkerOnMap === "function") {
                console.log("Map ready. Showing SOS marker");
                window.showSOSMarkerOnMap(sosData);
                sessionStorage.removeItem("pendingSOSLocation");
                clearInterval(interval);
            }

            attempts++;
            if (attempts > 15) {
                console.warn("Map not ready after retries");
                clearInterval(interval);
            }
        }, 300);
    } catch (err) {
        console.error("Error parsing pending SOS location:", err);
        sessionStorage.removeItem("pendingSOSLocation");
    }
}

window.addEventListener("load", waitForMapAndShowSOS);

// Consolidated Global Click Handler (Fixes duplicate markers/logs)
document.onclick = function (e) {
    const btn = e.target.closest(".view-sos-map");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    console.log("View on Map clicked");

    const sosData = {
        latitude: parseFloat(btn.dataset.lat),
        longitude: parseFloat(btn.dataset.lng),
        username: btn.dataset.username,
        emergency_contact_phone: btn.dataset.phone,
        created_at: btn.dataset.time
    };

    console.log("SOS map data:", sosData);

    if (!sosData.latitude || !sosData.longitude) {
        alert("SOS location is not available.");
        return;
    }

    sessionStorage.setItem("pendingSOSLocation", JSON.stringify(sosData));

    if (window.map && typeof window.showSOSMarkerOnMap === "function") {
        window.showSOSMarkerOnMap(sosData);
    } else {
        console.log("Redirecting to dashboard...");
        window.location.href = "/dashboard/";
    }
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// SOS Logic
async function triggerSOS() {
    console.log("SOS clicked");
    // Vibrate device if supported
    if (navigator.vibrate) {
        navigator.vibrate([500, 200, 500, 200, 500]);
    }

    if ("geolocation" in navigator) {
        console.log("Requesting geolocation for SOS...");
        navigator.geolocation.getCurrentPosition(async position => {
            console.log("geolocation success");
            const payload = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                ride_id: null
            };
            
            // Try to find if user has an active ride to include it
            try {
                const response = await fetch('/api/rides/my-offered/');
                const rides = await response.json();
                const activeRide = rides.find(r => ['active', 'ongoing'].includes(r.status));
                if (activeRide) {
                    payload.ride_id = activeRide.id;
                    console.log("Active ride found and added to payload:", activeRide.id);
                }
            } catch (err) {
                console.warn("Could not fetch active ride for SOS payload", err);
            }

            sendSOSPayload(payload);
        }, error => {
            console.log("geolocation error:", error.message);
            if (error.code === error.PERMISSION_DENIED) {
                alert("Location permission is required to send SOS.");
            } else {
                alert("Unable to retrieve your location for SOS.");
            }
        }, { timeout: 10000, enableHighAccuracy: true });
    } else {
        alert("Geolocation is not supported by your browser. SOS cannot be sent with location.");
    }
}

async function sendSOSPayload(payload) {
    console.log("SOS payload:", payload);
    const csrftoken = getCookie('csrftoken');
    
    try {
        const response = await fetch('/api/sos/trigger/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin',
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        console.log("SOS response status:", response.status);
        console.log("SOS response:", data);
        
        if(response.ok && data.success === true) {
            alert("SOS sent");
            if (data.emergency_contact_phone) {
                console.log("SOS sent to emergency contact:", data.emergency_contact_phone);
            }
        } else {
            const errorMsg = data.message || "Failed to trigger SOS. Please call emergency services directly.";
            alert(`Error: ${errorMsg}`);
        }
    } catch (error) {
        console.error('Network error during SOS trigger:', error);
        alert("Failed to send SOS due to network error. Please call emergency services directly.");
    }
}

// WebSocket Logic for SOS Alerts
let sosSocket = null;

function connectSOSSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${protocol}://${window.location.host}/ws/sos/`;
    
    console.log("Connecting to SOS WebSocket:", socketUrl);
    sosSocket = new WebSocket(socketUrl);

    sosSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log("Real-time SOS Alert Received:", data);
        
        // Show notification/alert
        showSOSAlert(data);
    };

    sosSocket.onclose = function(e) {
        console.error("SOS Socket closed unexpectedly. Reconnecting in 3 seconds...");
        setTimeout(connectSOSSocket, 3000);
    };

    sosSocket.onerror = function(err) {
        console.error("SOS Socket error:", err);
    };
}

function showSOSAlert(data) {
    // Show a stylized toast or alert
    const toast = document.createElement('div');
    toast.className = 'sos-alert-toast';
    toast.innerHTML = `
        <div class="sos-alert-header">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <span>EMERGENCY SOS ALERT</span>
        </div>
        <div class="sos-alert-body">
            <strong>${data.username}</strong> needs help!<br>
            <small>Contact: ${data.emergency_contact_phone}</small>
        </div>
        <div class="sos-alert-footer">
            <button class="primary-btn btn-ripple view-sos-map" 
                data-lat="${data.latitude}" 
                data-lng="${data.longitude}" 
                data-username="${data.username}" 
                data-phone="${data.emergency_contact_phone || ''}" 
                data-time="${data.created_at || ''}"
                style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">
                View on Map
            </button>
            <button onclick="this.parentElement.parentElement.remove()" class="icon-btn" style="color: white;"><i class="bi bi-x"></i></button>
        </div>
    `;
    document.body.appendChild(toast);
    
    // Play sound if possible
    try {
        const audio = new Audio("https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3");
        audio.play().catch(() => console.warn("SOS sound not available"));
    } catch (e) {
        console.warn("SOS sound skipped", e);
    }

    // Auto remove after 15 seconds
    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 15000);

    // If map exists on this page, add marker automatically
    if (window.map) {
        window.showSOSMarkerOnMap(data);
    }
}

// Marker Replacement Logic (Global Function)
window.showSOSMarkerOnMap = function (data) {
    if (!window.map || typeof L === "undefined") {
        console.warn("Map not ready");
        return;
    }

    const lat = parseFloat(data.latitude);
    const lng = parseFloat(data.longitude);

    console.log("Showing marker at:", lat, lng);

    window.map.setView([lat, lng], 16);

    // Remove old marker before adding a new one
    if (window.currentSOSMarker) {
        window.map.removeLayer(window.currentSOSMarker);
    }

    const sosIcon = L.divIcon({
        className: 'sos-marker-container',
        html: '<div class="sos-marker"></div>',
        iconSize: [30, 30]
    });

    window.currentSOSMarker = L.marker([lat, lng], {icon: sosIcon, title: "SOS Alert"}).addTo(window.map);

    window.currentSOSMarker.bindPopup(`
        <div style="color: black;">
            <strong>🚨 SOS ALERT</strong><br>
            User: ${data.username}<br>
            Contact: ${data.emergency_contact_phone || "N/A"}<br>
            Time: ${data.created_at || ""}
        </div>
    `).openPopup();
};
