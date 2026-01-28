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
import type { User, NavItem } from "../../types";
import { fetchLawyers, type Lawyer } from "../../services/lawyers";

export interface LawyerFinderPageProps {
  user: User;
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

  // Fetch lawyers from the backend
  useEffect(() => {
    const loadLawyers = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchLawyers(selectedSpecialization || undefined);
        setLawyers(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch lawyers",
        );
        console.error("Error fetching lawyers:", err);
      } finally {
        setLoading(false);
      }
    };

    loadLawyers();
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

  const filteredLawyers = lawyers.filter((lawyer) => {
    const matchesSearch =
      lawyer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lawyer.specialties.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

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
        </p>
        <div className="flex items-center gap-2">
          <Icon name="MapPin" size="sm" className="text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            Based on your location
          </span>
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

      {/* Empty state */}
      {!loading && filteredLawyers.length === 0 && !error && (
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
            }}
          >
            Clear Filters
          </Button>
        </div>
      )}

      {/* Map placeholder */}
      <Card
        variant="default"
        padding="none"
        className="mt-6 overflow-hidden animate-slide-up"
      >
        <div className="h-64 bg-secondary/50 flex items-center justify-center border-b border-border">
          <div className="text-center">
            <Icon
              name="Map"
              size="xl"
              className="text-muted-foreground/50 mx-auto mb-3"
            />
            <p className="text-sm text-muted-foreground">
              Map view coming soon
            </p>
            <p className="text-xs text-muted-foreground/80 mt-1">
              Interactive map showing lawyer locations
            </p>
          </div>
        </div>
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon name="MapPin" size="sm" className="text-purple-400" />
            <span className="text-sm text-muted-foreground">
              Your location: Detected automatically
            </span>
          </div>
          <Button variant="ghost" size="sm">
            <Icon name="RefreshCw" size="xs" />
            Update
          </Button>
        </div>
      </Card>
    </DashboardLayout>
  );
}

export default LawyerFinderPage;
