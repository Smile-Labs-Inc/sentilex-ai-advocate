// =============================================================================
// LawyerMap Component
// Interactive map showing lawyer locations by district
// =============================================================================

import { useEffect, useRef } from "preact/hooks";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { DistrictLawyers } from "../../../services/lawyers";
import { Icon } from "../../atoms/Icon/Icon";
import { SRI_LANKA_CENTER } from "../../../data/districtCoordinates";

// Fix for default marker icons in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Add custom CSS for popups
if (
  typeof document !== "undefined" &&
  !document.getElementById("lawyer-map-styles")
) {
  const style = document.createElement("style");
  style.id = "lawyer-map-styles";
  style.textContent = `
    .lawyer-popup .leaflet-popup-content-wrapper {
      border-radius: 12px;
      padding: 0;
      background: #18181b;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }
    .lawyer-popup .leaflet-popup-content {
      margin: 0;
      width: auto !important;
    }
    .lawyer-popup .leaflet-popup-tip {
      background: #18181b;
    }
    .lawyer-popup .leaflet-popup-close-button {
      color: #ffffff !important;
      font-size: 20px !important;
      padding: 4px 8px !important;
    }
    .lawyer-popup .leaflet-popup-close-button:hover {
      color: #a1a1aa !important;
    }
    .lawyer-pin {
      transition: transform 0.2s;
    }
    .lawyer-pin:hover {
      transform: scale(1.1);
    }
  `;
  document.head.appendChild(style);
}

export interface LawyerMapProps {
  districtData: DistrictLawyers[];
  onDistrictClick?: (district: DistrictLawyers) => void;
  selectedDistrict?: string | null;
  height?: string;
}

export function LawyerMap({
  districtData,
  onDistrictClick,
  selectedDistrict,
  height = "500px",
}: LawyerMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const markersLayer = useRef<L.LayerGroup | null>(null);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) return;

    // Create map centered on Sri Lanka
    const map = L.map(mapContainer.current).setView(
      [SRI_LANKA_CENTER.latitude, SRI_LANKA_CENTER.longitude],
      7,
    );

    // Add tile layer
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    mapInstance.current = map;
    markersLayer.current = L.layerGroup().addTo(map);

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // Update markers when district data changes
  useEffect(() => {
    if (!mapInstance.current || !markersLayer.current) return;

    // Clear existing markers
    markersLayer.current.clearLayers();

    // Add individual markers for each lawyer
    districtData.forEach((district) => {
      district.lawyers.forEach((lawyer) => {
        // Add small random offset so lawyers in same district don't overlap
        const latOffset = (Math.random() - 0.5) * 0.05;
        const lngOffset = (Math.random() - 0.5) * 0.05;

        // Create custom pin icon
        const iconHtml = `
          <div style="
            background: ${lawyer.availability === "Available" ? "#10b981" : lawyer.availability === "In Consultation" ? "#f59e0b" : "#6b7280"};
            color: white;
            border-radius: 50% 50% 50% 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            transform: rotate(-45deg);
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          ">
            <span style="transform: rotate(45deg); font-size: 16px;">⚖️</span>
          </div>
        `;

        const customIcon = L.divIcon({
          html: iconHtml,
          className: "lawyer-pin",
          iconSize: [30, 30],
          iconAnchor: [15, 30],
          popupAnchor: [0, -30],
        });

        // Create marker
        const marker = L.marker(
          [district.latitude + latOffset, district.longitude + lngOffset],
          { icon: customIcon },
        );

        // Get lawyer initials
        const initials = lawyer.name
          .split(" ")
          .map((n) => n[0])
          .join("")
          .slice(0, 2);

        // Availability status
        const availabilityColor =
          lawyer.availability === "Available"
            ? "#10b981"
            : lawyer.availability === "In Consultation"
              ? "#f59e0b"
              : "#6b7280";

        const availabilityText =
          lawyer.availability === "Available"
            ? "🟢 Available Now"
            : lawyer.availability === "In Consultation"
              ? "🟡 In Consultation"
              : "⚫ Offline";

        // Specialties
        const specialties = lawyer.specialties.split(",").map((s) => s.trim());
        const specialtyTags = specialties
          .map(
            (spec) =>
              `<span style="background: #27272a; color: #d4d4d8; padding: 4px 10px; border-radius: 6px; font-size: 11px; margin-right: 4px; display: inline-block; margin-bottom: 4px; border: 1px solid #3f3f46;">${spec}</span>`,
          )
          .join("");

        // Create detailed popup
        const popupContent = `
          <div style="padding: 16px; min-width: 280px; font-family: system-ui, -apple-system, sans-serif; background: #18181b; border-radius: 12px;">
            <!-- Header -->
            <div style="display: flex; gap: 12px; margin-bottom: 12px;">
              <div style="
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: linear-gradient(135deg, #8b5cf6, #6366f1);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 18px;
                flex-shrink: 0;
              ">
                ${initials}
              </div>
              <div style="flex: 1; min-width: 0;">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                  <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #ffffff;">${lawyer.name}</h3>
                  ${lawyer.rating >= 4.5 ? '<span style="color: #3b82f6; font-size: 16px;">✓</span>' : ""}
                </div>
                <p style="margin: 0; font-size: 13px; color: ${availabilityColor}; font-weight: 500;">
                  ${availabilityText}
                </p>
              </div>
            </div>

            <!-- Rating -->
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #27272a;">
              <div style="display: flex; align-items: center; gap: 4px;">
                <span style="color: #fbbf24; font-size: 14px;">⭐</span>
                <span style="font-weight: 600; color: #ffffff; font-size: 14px;">${lawyer.rating.toFixed(1)}</span>
              </div>
              <span style="color: #a1a1aa; font-size: 13px;">${lawyer.reviews_count} reviews</span>
            </div>

            <!-- Specialties -->
            <div style="margin-bottom: 12px;">
              ${specialtyTags}
            </div>

            <!-- Details -->
            <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; font-size: 13px; color: #a1a1aa;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span>📍</span>
                <span>${lawyer.district}</span>
              </div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span>💼</span>
                <span>${lawyer.experience_years} years</span>
              </div>
            </div>

            <!-- Actions -->
            <div style="display: flex; gap: 8px;">
              <button
                onclick="window.open('mailto:${lawyer.email}', '_blank')"
                style="
                  flex: 1;
                  background: #ffffff;
                  color: #18181b;
                  border: none;
                  padding: 10px 16px;
                  border-radius: 8px;
                  cursor: pointer;
                  font-size: 13px;
                  font-weight: 500;
                  transition: background 0.2s;
                "
                onmouseover="this.style.background='#f4f4f5'"
                onmouseout="this.style.background='#ffffff'"
                ${lawyer.availability === "Offline" ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ""}
              >
                💬 Contact
              </button>
              <button
                onclick="alert('Profile view coming soon!')"
                style="
                  background: #27272a;
                  color: #ffffff;
                  border: 1px solid #3f3f46;
                  padding: 10px 16px;
                  border-radius: 8px;
                  cursor: pointer;
                  font-size: 13px;
                  font-weight: 500;
                  transition: background 0.2s;
                "
                onmouseover="this.style.background='#3f3f46'"
                onmouseout="this.style.background='#27272a'"
              >
                👤 Profile
              </button>
            </div>
          </div>
        `;

        marker.bindPopup(popupContent, {
          maxWidth: 300,
          className: "lawyer-popup",
        });

        marker.addTo(markersLayer.current!);
      });
    });
  }, [districtData, selectedDistrict, onDistrictClick]);

  return (
    <div className="relative">
      <div
        ref={mapContainer}
        style={{ height, width: "100%" }}
        className="rounded-lg overflow-hidden border border-border"
      />

      {/* Map controls overlay */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
        <button
          onClick={() => {
            if (mapInstance.current) {
              mapInstance.current.setView(
                [SRI_LANKA_CENTER.latitude, SRI_LANKA_CENTER.longitude],
                7,
              );
            }
          }}
          className="bg-background/90 backdrop-blur-sm border border-border rounded-lg p-2 hover:bg-secondary transition-colors"
          title="Reset view"
        >
          <Icon name="Home" size="sm" />
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-background/90 backdrop-blur-sm border border-border rounded-lg p-3">
        <h4 className="text-xs font-semibold text-foreground mb-2">
          Lawyer Status
        </h4>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border border-white"></div>
            <span className="text-xs text-muted-foreground">Available</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500 border border-white"></div>
            <span className="text-xs text-muted-foreground">
              In Consultation
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gray-500 border border-white"></div>
            <span className="text-xs text-muted-foreground">Offline</span>
          </div>
        </div>
      </div>
    </div>
  );
}
