import { Button } from "../../atoms/Button/Button";
import { Icon } from "../../atoms/Icon/Icon";
import { ActivityFeed } from "../ActivityFeed/ActivityFeed";
import type { ActivityItem as ActivityItemType } from "../../../types";

export interface ActivityModalProps {
  isOpen: boolean;
  activities: ActivityItemType[];
  onClose: () => void;
}

export function ActivityModal({
  isOpen,
  activities,
  onClose,
}: ActivityModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal Panel near top-center, wider and scrollable */}
      <div className="relative mt-8 w-full max-w-3xl animate-scale-in">
        <div className="p-6 bg-background/70 rounded-lg border border-border max-h-[70vh] w-full overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Icon name="Activity" className="text-muted-foreground" />
              <h3 className="text-sm font-semibold text-foreground">
                Recent Activity
              </h3>
            </div>

            <Button variant="ghost" onClick={onClose}>
              <Icon name="X" />
            </Button>
          </div>

          <ActivityFeed activities={activities} className="w-full" />
        </div>
      </div>
    </div>
  );
}

export default ActivityModal;
