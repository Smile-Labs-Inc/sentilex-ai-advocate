// =============================================================================
// Sample Notification Data
// Example data structure and usage for the NotificationBell component
// =============================================================================

import type { Notification } from '../types';

// Sample notification data matching the professional legal context
export const sampleNotifications: Notification[] = [
    {
        id: '1',
        title: 'Case Update Required',
        message: 'Please review and update evidence documentation for Case #2024-001.',
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
        isRead: false,
        type: 'case'
    },
    {
        id: '2',
        title: 'Legal Consultation Scheduled',
        message: 'Your consultation with Smith & Associates is confirmed for tomorrow at 2:00 PM.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
        isRead: false,
        type: 'legal'
    },
    {
        id: '3',
        message: 'System maintenance will occur tonight from 11 PM to 1 AM EST.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
        isRead: true,
        type: 'system'
    },
    {
        id: '4',
        title: 'Document Verification Complete',
        message: 'All submitted documents have been verified and processed successfully.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
        isRead: true,
        type: 'account'
    },
    {
        id: '5',
        title: 'Regulatory Update',
        message: 'New privacy regulations effective next month may impact your case strategy.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
        isRead: false,
        type: 'legal'
    }
];

// Example integration in a React component
export const ExampleUsage = `
import { useState } from 'preact/hooks';
import { NotificationBell } from '../components/molecules/NotificationBell/NotificationBell';
import { sampleNotifications } from '../data/sampleNotifications';

export function MyComponent() {
  const [notifications, setNotifications] = useState(sampleNotifications);

  const handleMarkAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, isRead: true }
          : notification
      )
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, isRead: true }))
    );
  };

  const handleViewAll = () => {
    // Navigate to notifications page
    
  };

  return (
    <div className="navbar">
      <NotificationBell
        notifications={notifications}
        onMarkAsRead={handleMarkAsRead}
        onMarkAllAsRead={handleMarkAllAsRead}
        onViewAll={handleViewAll}
      />
    </div>
  );
}
`;