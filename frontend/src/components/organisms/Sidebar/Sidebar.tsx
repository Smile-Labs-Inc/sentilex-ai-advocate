// =============================================================================
// Sidebar Organism
// Full navigation sidebar with search, nav items, and user profile
// =============================================================================

import { useState } from "preact/hooks";
import { cn } from "../../../lib/utils";
import { Icon } from "../../atoms/Icon/Icon";
import { Button } from "../../atoms/Button/Button";
import { ThemeToggle } from "../../atoms/ThemeToggle/ThemeToggle";
import { SearchInput } from "../../molecules/SearchInput/SearchInput";
import { NavItem } from "../../molecules/NavItem/NavItem";
import { UserProfile } from "../../molecules/UserProfile/UserProfile";
import { mainNavigation } from "../../../data/navigation";
import { useTheme } from "../../../hooks/useTheme";
import type { NavItem as NavItemType } from "../../../types";
import type { UserProfile as AuthUserProfile } from "../../../types/auth";
import { UpgradeModal } from "../UpgradeModal/UpgradeModal";

export interface SidebarProps {
  user: AuthUserProfile;
  currentPath?: string;
  onNavigate?: (item: NavItemType) => void;
  className?: string;
}

export function Sidebar({
  user,
  currentPath = "/",
  onNavigate,
  className,
}: SidebarProps) {
  const [activeItem, setActiveItem] = useState(currentPath);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const { resolvedTheme, toggleTheme } = useTheme();

  const handleNavClick = (item: NavItemType) => {
    setActiveItem(item.href);
    onNavigate?.(item);
  };

  return (
    <>
      <aside
        className={cn(
          "w-64 flex flex-col h-full",
          "w-64 flex flex-col h-full",
          "bg-background/80 backdrop-blur-md border-r border-border",
          "flex-shrink-0",
          className,
        )}
      >
        {/* Logo */}
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-foreground font-bold text-lg tracking-wider">
            <Icon name="Scale" size="md" />
            <span className="font-['Space_Grotesk']">VERITAS</span>
          </div>
          <button className="p-1.5 hover:bg-secondary rounded-lg transition-colors">
            <Icon
              name="PanelLeftClose"
              size="sm"
              className="text-muted-foreground"
            />
          </button>
        </div>

        {/* Search */}
        <div className="px-4 mb-4">
          <SearchInput placeholder="Search here..." />
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 space-y-1">
          {mainNavigation.map((section, sectionIndex) => (
            <div key={sectionIndex}>
              {/* Section title */}
              {section.title && (
                <div className="pt-4 pb-2 px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {section.title}
                </div>
              )}

              {/* Nav items */}
              <div className="space-y-1">
                {section.items.map((item) => (
                  <NavItem
                    key={item.id}
                    item={item}
                    isActive={activeItem === item.href}
                    onClick={handleNavClick}
                  />
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Upgrade CTA & Theme Toggle */}
        <div className="p-4 border-t border-border">
          <div className="bg-linear-to-br from-secondary to-background border border-border rounded-xl p-4 mb-4">
            <div className="flex items-center gap-2 text-foreground mb-2">
              <Icon name="Crown" size="sm" className="text-yellow-500" />
              <span className="text-xs font-bold">Upgrade to Pro</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed mb-3">
              Get priority AI support and unlimited case storage
            </p>
            <Button
              size="sm"
              className="w-full text-xs font-bold"
              onClick={() => setIsUpgradeModalOpen(true)}
            >
              UPGRADE PLAN
            </Button>
          </div>

          {/* Theme Toggle & User Profile */}
          <div className="flex items-center gap-2 mb-2">
            <ThemeToggle
              theme={resolvedTheme}
              onToggle={toggleTheme}
              size="sm"
              className="shrink-0"
            />
            <span className="text-xs text-muted-foreground">
              {resolvedTheme === "dark" ? "Dark" : "Light"} mode
            </span>
          </div>

          {/* User Profile */}
          <UserProfile user={user} variant="expanded" />
        </div>
      </aside>

      {/* Upgrade Modal - Rendered outside sidebar */}
      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
      />
    </>
  );
}
