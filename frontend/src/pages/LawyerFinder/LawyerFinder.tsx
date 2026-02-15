// =============================================================================
// LawyerFinder Page
// Find nearby lawyers for legal consultation
// =============================================================================

import { useState, useEffect } from "preact/hooks";
import { DashboardLayout } from "../../components/templates/DashboardLayout/DashboardLayout";
import { Card } from "../../components/atoms/Card/Card";
import { Button } from "../../components/atoms/Button/Button";
import { Icon } from "../../components/atoms/Icon/Icon";
import { Input } from "../../components/atoms/Input/Input";
import { Badge } from "../../components/atoms/Badge/Badge";
import type { NavItem } from "../../types";
import type { UserProfile } from "../../types/auth";
import {
  fetchLawyers,
  type Lawyer,
  type DistrictLawyers,
  lawyerService,
} from "../../services/lawyers";
import { MOCK_LAWYERS } from "../../data/mockLayers";
import { LawyerMap } from "../../components/molecules/LawyerMap/LawyerMap";

export interface LawyerFinderPageProps {
  user: UserProfile;
  onNavigate: (item: NavItem) => void;
  onBack: () => void;
}

const availabilityConfig: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  Available: {
    label: "Available Now",
    color: "text-green-400",
    bg: "bg-green-500",
  },
  "In Consultation": {
    label: "In Consultation",
    color: "text-yellow-400",
    bg: "bg-yellow-500",
  },
  Offline: {
    label: "Offline",
    color: "text-muted-foreground",
    bg: "bg-muted-foreground",
  },
};

export function LawyerFinderPage({
  user,
  onNavigate,
  onBack,
}: LawyerFinderPageProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSpecialization, setSelectedSpecialization] = useState<
    string | null
  >(null);
  const [lawyers, setLawyers] = useState<Lawyer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "map">("list");
  const [mapData, setMapData] = useState<DistrictLawyers[]>([]);
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);

  // Fetch lawyers from the backend
  useEffect(() => {
    const loadLawyers = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchLawyers(selectedSpecialization || undefined);

        if (data.length === 0) {
          setLawyers(MOCK_LAWYERS);
        } else {
          setLawyers(data);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch lawyers",
        );
      } finally {
        setLoading(false);
      }
    };

    loadLawyers();
  }, [selectedSpecialization]);

  // Fetch map data
  useEffect(() => {
    const loadMapData = async () => {
      try {
        const data = await lawyerService.getLawyersByDistrictMap(
          selectedSpecialization || undefined,
        );

        // If backend returns empty data, use mock lawyers
        if (!data || data.length === 0) {
          // Fallback: Group MOCK_LAWYERS by district
          const grouped: Record<string, Lawyer[]> = {};
          MOCK_LAWYERS.forEach((lawyer) => {
            if (!grouped[lawyer.district]) {
              grouped[lawyer.district] = [];
            }
            grouped[lawyer.district].push(lawyer);
          });

          // Import district coordinates
          const { DISTRICT_COORDINATES } =
            await import("../../data/districtCoordinates");

          // Convert to DistrictLawyers format with real coordinates
          const mockMapData: DistrictLawyers[] = Object.entries(grouped).map(
            ([district, districtLawyers]) => {
              const coords = DISTRICT_COORDINATES[district] || {
                latitude: 7.8731,
                longitude: 80.7718,
              };
              return {
                district,
                latitude: coords.latitude,
                longitude: coords.longitude,
                lawyer_count: districtLawyers.length,
                lawyers: districtLawyers,
              };
            },
          );
          setMapData(mockMapData);
        } else {
          setMapData(data);
        }
      } catch (err) {
        console.error("Failed to load map data:", err);
        // Fallback: Group MOCK_LAWYERS by district
        const grouped: Record<string, Lawyer[]> = {};
        MOCK_LAWYERS.forEach((lawyer) => {
          if (!grouped[lawyer.district]) {
            grouped[lawyer.district] = [];
          }
          grouped[lawyer.district].push(lawyer);
        });

        // Convert to DistrictLawyers format with mock coordinates
        const mockMapData: DistrictLawyers[] = Object.entries(grouped).map(
          ([district, districtLawyers]) => ({
            district,
            latitude: 7.8731,
            longitude: 80.7718,
            lawyer_count: districtLawyers.length,
            lawyers: districtLawyers,
          }),
        );
        setMapData(mockMapData);
      }
    };

    loadMapData();
  }, [selectedSpecialization]);

  // Get unique specializations from all lawyers
  const specializations = [
    "All",
    ...Array.from(
      new Set(
        lawyers.flatMap((lawyer) =>
          lawyer.specialties.split(",").map((s) => s.trim()),
        ),
      ),
    ),
  ];

  const filteredLawyers = lawyers
    .filter((lawyer) => {
      const matchesSearch =
        lawyer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        lawyer.specialties.toLowerCase().includes(searchQuery.toLowerCase());

      // Filter by specialization if selected (for mock data or client-side filtering)
      const matchesSpecialization =
        !selectedSpecialization ||
        selectedSpecialization === "All" ||
        lawyer.specialties.includes(selectedSpecialization);

      // Filter by district if selected from map
      const matchesDistrict =
        !selectedDistrict || lawyer.district === selectedDistrict;

      return matchesSearch && matchesSpecialization && matchesDistrict;
    })
    .slice(0, 6);

  const handleDistrictClick = (district: DistrictLawyers) => {
    setSelectedDistrict(district.district);
    setViewMode("list");
    // Scroll to lawyers list
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <DashboardLayout user={user} currentPath="/lawyers" onNavigate={onNavigate}>
      {/* Header */}
      <div className="mb-6 animate-fade-in">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={onBack}
            className="shrink-0"
          >
            <Icon name="ArrowLeft" size="sm" />
          </Button>
          <div>
            <h1 className="text-2xl font-semibold text-foreground">
              Find a Lawyer
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Connect with verified legal professionals in your area
            </p>
          </div>
        </div>
      </div>

      {/* Search and filters */}
      <Card variant="default" padding="lg" className="mb-6 animate-slide-up">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search by name or specialization..."
              value={searchQuery}
              onInput={(e) =>
                setSearchQuery((e.target as HTMLInputElement).value)
              }
              className="w-full"
            />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {specializations.map((spec) => (
              <button
                key={spec}
                onClick={() =>
                  setSelectedSpecialization(spec === "All" ? null : spec)
                }
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  (spec === "All" && !selectedSpecialization) ||
                  selectedSpecialization === spec
                    ? "bg-foreground text-background"
                    : "bg-secondary text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                {spec}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Results count */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {loading
            ? "Loading..."
            : `${filteredLawyers.length} lawyer${filteredLawyers.length !== 1 ? "s" : ""} found`}
          {selectedDistrict && (
            <span className="ml-2">
              in{" "}
              <button
                onClick={() => setSelectedDistrict(null)}
                className="text-purple-400 hover:text-purple-300 underline"
              >
                {selectedDistrict} ×
              </button>
            </span>
          )}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === "list" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setViewMode("list")}
          >
            <Icon name="List" size="xs" />
            List
          </Button>
          <Button
            variant={viewMode === "map" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setViewMode("map")}
          >
            <Icon name="Map" size="xs" />
            Map
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <Card
          variant="default"
          padding="lg"
          className="mb-4 bg-red-500/10 border-red-500/20"
        >
          <div className="flex items-center gap-3">
            <Icon name="AlertCircle" size="sm" className="text-red-400" />
            <div>
              <h3 className="text-sm font-medium text-red-400">
                Error loading lawyers
              </h3>
              <p className="text-xs text-red-400/80 mt-1">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Lawyers list */}
      {viewMode === "list" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredLawyers.map((lawyer) => {
            const availability =
              availabilityConfig[lawyer.availability] ||
              availabilityConfig["Available"];
            const specialtiesList = lawyer.specialties
              .split(",")
              .map((s) => s.trim());

            return (
              <Card
                key={lawyer.id}
                variant="interactive"
                padding="lg"
                className="animate-slide-up"
              >
                <div className="flex gap-4">
                  {/* Avatar */}
                  <div className="relative">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-xl font-semibold">
                      {lawyer.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                        .slice(0, 2)}
                    </div>
                    {/* Availability dot */}
                    <div
                      className={`absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-background ${availability.bg}`}
                    />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
                          {lawyer.name}
                          {lawyer.rating >= 4.5 && (
                            <Icon
                              name="BadgeCheck"
                              size="xs"
                              className="text-blue-400"
                            />
                          )}
                        </h3>
                        <p className={`text-xs ${availability.color}`}>
                          {availability.label}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-1">
                          <Icon
                            name="Star"
                            size="xs"
                            className="text-yellow-400"
                          />
                          <span className="text-sm font-medium text-foreground">
                            {lawyer.rating.toFixed(1)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {lawyer.reviews_count} reviews
                        </p>
                      </div>
                    </div>

                    {/* Specializations */}
                    <div className="flex flex-wrap gap-1 mt-2">
                      {specialtiesList.map((spec) => (
                        <Badge
                          key={spec}
                          variant="outline"
                          className="text-[10px]"
                        >
                          {spec}
                        </Badge>
                      ))}
                    </div>

                    {/* Meta */}
                    <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Icon name="MapPin" size="xs" />
                        {lawyer.district}
                      </span>
                      <span className="flex items-center gap-1">
                        <Icon name="Briefcase" size="xs" />
                        {lawyer.experience_years} years
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 mt-4">
                      <Button
                        variant="primary"
                        size="sm"
                        className="flex-1"
                        disabled={lawyer.availability === "Offline"}
                      >
                        <Icon name="MessageCircle" size="xs" />
                        Contact
                      </Button>
                      <Button variant="secondary" size="sm">
                        <Icon name="User" size="xs" />
                        Profile
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {viewMode === "list" &&
        !loading &&
        filteredLawyers.length === 0 &&
        !error && (
          <div className="text-center py-12">
            <Icon
              name="Scale"
              size="xl"
              className="text-muted-foreground/50 mx-auto mb-4"
            />
            <h3 className="text-lg font-medium text-foreground mb-2">
              No lawyers found
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Try adjusting your search or filters
            </p>
            <Button
              variant="secondary"
              onClick={() => {
                setSearchQuery("");
                setSelectedSpecialization(null);
                setSelectedDistrict(null);
              }}
            >
              Clear Filters
            </Button>
          </div>
        )}

      {/* Map view */}
      {viewMode === "map" && (
        <Card
          variant="default"
          padding="none"
          className="overflow-hidden animate-slide-up"
        >
          <div className="p-4 border-b border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Icon name="MapPin" size="sm" className="text-purple-400" />
                <span className="text-sm font-medium text-foreground">
                  Lawyer Locations
                </span>
                <Badge variant="outline" className="text-xs">
                  {mapData.reduce((sum, d) => sum + d.lawyer_count, 0)} lawyers
                  across {mapData.length} districts
                </Badge>
              </div>
              <span className="text-xs text-muted-foreground">
                Click on a pin to view lawyer details
              </span>
            </div>
          </div>
          <LawyerMap
            districtData={mapData}
            onDistrictClick={handleDistrictClick}
            selectedDistrict={selectedDistrict}
            height="600px"
          />
        </Card>
      )}
    </DashboardLayout>
  );
}

export default LawyerFinderPage;
