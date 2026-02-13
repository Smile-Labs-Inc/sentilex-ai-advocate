// =============================================================================
// DashboardLayout Template
// Main layout with sidebar and scrollable content area
// =============================================================================

import { useState } from "preact/hooks";
import { cn } from "../../../lib/utils";
import { Sidebar } from "../../organisms/Sidebar/Sidebar";
import { Icon } from "../../atoms/Icon/Icon";
import { BackgroundGradientAnimation } from "../../atoms/BackgroundGradientAnimation/BackgroundGradientAnimation";
import type { NavItem } from "../../../types";
import type { UserProfile } from "../../../types/auth";
import type { ComponentChildren } from "preact";

export interface DashboardLayoutProps {
  user: UserProfile;
  currentPath?: string;
  onNavigate?: (item: NavItem) => void;
  onOpenActivity?: () => void;
  children: ComponentChildren;
  className?: string;
}

export function DashboardLayout({
  user,
  currentPath = "/",
  onNavigate,
  onOpenActivity,
  children,
  className,
}: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setSidebarCollapsed((prev) => !prev);
  };

  return (
    <BackgroundGradientAnimation
      containerClassName="flex h-screen overflow-hidden"
      className="flex h-full w-full relative z-10"
      gradientBackgroundStart="rgb(0, 0, 0)"
      gradientBackgroundEnd="rgb(0, 0, 0)"
      firstColor="4, 23, 51"
      secondColor="51, 13, 13"
      thirdColor="51, 32, 24"
      fourthColor="44, 15, 51"
      fifthColor="20, 44, 51"
      pointerColor="28, 20, 51"
      interactive={false}
    >
      {/* Sidebar with Glass Effect */}
      <div
        className="h-full relative z-20 transition-all duration-300 ease-in-out overflow-hidden"
        style={{ width: sidebarCollapsed ? '0px' : '16rem', minWidth: sidebarCollapsed ? '0px' : '16rem' }}
      >
        <Sidebar
          user={user}
          currentPath={currentPath}
          onNavigate={onNavigate}
          onOpenActivity={onOpenActivity}
          onToggleSidebar={handleToggleSidebar}
          className="bg-transparent/40 md:bg-black/20 backdrop-blur-xl border-r border-white/10"
        />
      </div>

      {/* Expand button when sidebar is collapsed */}
      {sidebarCollapsed && (
        <button
          onClick={handleToggleSidebar}
          className="absolute top-4 left-4 z-30 p-2 bg-black/40 backdrop-blur-md border border-white/10 rounded-lg hover:bg-black/60 transition-colors"
          aria-label="Expand sidebar"
        >
          <Icon name="PanelLeftOpen" size="sm" className="text-muted-foreground" />
        </button>
      )}

      {/* Main content area */}
      <main
        className={cn(
          "flex-1 overflow-y-auto relative z-10 bg-transparent",
          className,
        )}
      >
        <div className={cn("p-8 min-h-full", sidebarCollapsed && "pl-16")}>{children}</div>
      </main>
    </BackgroundGradientAnimation>
  );
}

export default DashboardLayout;
