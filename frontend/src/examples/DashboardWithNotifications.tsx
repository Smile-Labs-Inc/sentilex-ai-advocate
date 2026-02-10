// =============================================================================
// Dashboard Integration Example
// Shows how to integrate the NotificationBell with real data
// =============================================================================

// import { useState } from "preact/hooks"; // Uncomment when needed
import { DashboardHeader } from "../components/organisms/DashboardHeader/DashboardHeaderEnhanced";
import { useNotifications } from "../hooks/useNotifications";
import { useAuth } from "../hooks/useAuth";
// import { useDashboardData } from "../hooks/useDashboardData"; // Uncomment when needed

export function DashboardWithNotifications() {
    const { user } = useAuth();
    // const { incidents, stats } = useDashboardData(); // Uncomment when needed

    // Use the notifications hook for real-time notification management
    const {
        notifications,
        markAsRead,
        markAllAsRead,
    } = useNotifications();

    // const [showNewIncidentModal, setShowNewIncidentModal] = useState(false); // Uncomment when modal is implemented

    const handleNewIncident = () => {
        // setShowNewIncidentModal(true); // Uncomment when modal is implemented
        
    };

    const handleViewAllNotifications = () => {
        // Navigate to dedicated notifications page
        window.location.href = '/notifications';
    };

    if (!user) {
        return <div>Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-background text-foreground">
            <div className="container mx-auto px-4 py-6">
                {/* Enhanced Header with Professional Notification Bell */}
                <DashboardHeader
                    user={user}
                    notifications={notifications}
                    onNewIncident={handleNewIncident}
                    onMarkNotificationAsRead={markAsRead}
                    onMarkAllNotificationsAsRead={markAllAsRead}
                    onViewAllNotifications={handleViewAllNotifications}
                />

                {/* Rest of dashboard content */}
                <div className="space-y-8">
                    {/* Dashboard content goes here */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Stats cards, incident lists, etc. */}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DashboardWithNotifications;