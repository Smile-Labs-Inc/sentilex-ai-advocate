// =============================================================================
// DashboardHeader Organism
// Welcome message, notifications, and primary action button
// =============================================================================

import { cn } from "../../../lib/utils";
import { Button } from "../../atoms/Button/Button";
import { Avatar } from "../../atoms/Avatar/Avatar";
import { Icon } from "../../atoms/Icon/Icon";
import type { UserProfile } from "../../../types/auth";

export interface DashboardHeaderProps {
  user: UserProfile;
  onNewIncident?: () => void;
  onOpenActivity?: () => void;
  className?: string;
}

export function DashboardHeader({
  user,
  onNewIncident,
  onOpenActivity,
  className,
}: DashboardHeaderProps) {
  const greeting = getGreeting();

  return (
    <header className={cn("flex justify-between items-start mb-8", className)}>
      {/* Left side - Welcome message + activity button */}
      <div className="flex items-start gap-3 animate-fade-in">
        <div>
          <div className="uppercase text-xs font-bold tracking-wider text-muted-foreground mb-1">
            Dashboard
          </div>
          <h1 className="text-2xl text-foreground font-medium mb-1">
            {`${greeting}, ${user.first_name} 👋`}
          </h1>
          <p className="text-muted-foreground text-sm">
            Let's protect your digital rights today.
          </p>
        </div>
      </div>

      {/* Right side - Actions */}
      <div
        className="flex items-center gap-4 animate-fade-in"
        style={{ animationDelay: "0.1s" }}
      >
        {/* Notifications */}
        <button className="relative w-9 h-9 flex items-center justify-center rounded-lg bg-secondary hover:bg-accent transition-colors">
          <Icon name="Bell" size="sm" className="text-muted-foreground" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* Activity button (moved here next to primary action) */}
        <button
          onClick={() => onOpenActivity?.()}
          className="w-9 h-9 flex items-center justify-center rounded-lg bg-secondary hover:bg-accent transition-colors"
          aria-label="Open recent activity"
        >
          <Icon name="Activity" size="sm" className="text-foreground" />
        </button>

        {/* Primary action */}
        <Button onClick={onNewIncident} className="gap-2">
          <Icon name="Plus" size="sm" />
          NEW INCIDENT
        </Button>
      </div>
    </header>
  );
}

// Get appropriate greeting based on time of day
function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default DashboardHeader;
