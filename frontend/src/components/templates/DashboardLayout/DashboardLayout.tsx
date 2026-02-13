// =============================================================================
// DashboardLayout Template
// Main layout with sidebar and scrollable content area
// =============================================================================

import { cn } from "../../../lib/utils";
import { Sidebar } from "../../organisms/Sidebar/Sidebar";
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
      <div className="h-full relative z-20">
        <Sidebar
          user={user}
          currentPath={currentPath}
          onNavigate={onNavigate}
          onOpenActivity={onOpenActivity}
          className="bg-transparent/40 md:bg-black/20 backdrop-blur-xl border-r border-white/10"
        />
      </div>

      {/* Main content area */}
      <main
        className={cn(
          "flex-1 overflow-y-auto relative z-10 bg-transparent",
          className,
        )}
      >
        <div className="p-8 min-h-full">{children}</div>
      </main>
    </BackgroundGradientAnimation>
  );
}

export default DashboardLayout;
