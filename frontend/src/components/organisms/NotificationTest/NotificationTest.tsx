/**
 * Notification Test Component
 * For testing WebSocket notifications and browser notifications
 */

import { useState } from 'preact/hooks';
import { Button } from '../../atoms/Button/Button';
import { webSocketNotificationService } from '../../../services/websocket-notification';
import { notificationService } from '../../../services/notification';
import { BrowserNotificationUtil } from '../../../lib/browser-notifications';

export function NotificationTest() {
    const [wsStatus, setWsStatus] = useState(webSocketNotificationService.getStatus());
    const [testResults, setTestResults] = useState<string[]>([]);

    const addResult = (result: string) => {
        setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
    };

    const testWebSocketConnection = () => {
        if (!webSocketNotificationService.isConnected()) {
            webSocketNotificationService.connect();
            addResult('Attempting to connect WebSocket...');
        } else {
            addResult('WebSocket already connected');
        }
        setWsStatus(webSocketNotificationService.getStatus());
    };

    const testBrowserNotifications = async () => {
        const permission = await BrowserNotificationUtil.requestPermission();

        if (permission === 'granted') {
            const success = BrowserNotificationUtil.showNotification('Test Notification', {
                body: 'This is a test notification from SentiLex',
                tag: 'test-notification'
            });
            addResult(success ? 'Browser notification sent' : 'Failed to send browser notification');
        } else {
            addResult(`Browser notifications not permitted: ${permission}`);
        }
    };

    const testAPINotification = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                addResult('No authentication token found');
                return;
            }

            const response = await fetch('http://127.0.0.1:8000/api/notifications/test/send?message=Test from frontend!', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                addResult(`API notification sent successfully (ID: ${result.id})`);
            } else {
                const errorText = await response.text();
                addResult(`API notification failed: ${response.status} - ${errorText}`);
            }
        } catch (error) {
            addResult(`API notification failed: ${error}`);
        }
    };

    const clearResults = () => {
        setTestResults([]);
    };

    return (
        <div className="notification-test bg-white rounded-lg shadow p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold mb-4">🔔 Notification System Test</h3>

            <div className="grid gap-4">
                {/* WebSocket Status */}
                <div className="border rounded p-4">
                    <h4 className="font-medium mb-2">WebSocket Connection</h4>
                    <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${wsStatus === 'connected' ? 'bg-green-500' :
                                wsStatus === 'connecting' ? 'bg-yellow-500' :
                                    wsStatus === 'disconnected' ? 'bg-red-500' :
                                        wsStatus === 'closing' ? 'bg-orange-500' :
                                            'bg-gray-500'
                            }`}></div>
                        <span className="text-sm">Status: {wsStatus}</span>
                    </div>
                    <Button
                        onClick={testWebSocketConnection}
                        className="mt-2"
                        size="sm"
                        variant="outline"
                    >
                        {wsStatus === 'connected' ? 'Reconnect' : 'Connect'} WebSocket
                    </Button>
                </div>

                {/* Browser Notifications */}
                <div className="border rounded p-4">
                    <h4 className="font-medium mb-2">Browser Notifications</h4>
                    <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${BrowserNotificationUtil.getPermissionStatus() === 'granted' ? 'bg-green-500' :
                                BrowserNotificationUtil.getPermissionStatus() === 'denied' ? 'bg-red-500' :
                                    BrowserNotificationUtil.getPermissionStatus() === 'default' ? 'bg-yellow-500' :
                                        'bg-gray-500'
                            }`}></div>
                        <span className="text-sm">
                            Permission: {BrowserNotificationUtil.getPermissionStatus()}
                        </span>
                    </div>
                    <Button
                        onClick={testBrowserNotifications}
                        className="mt-2"
                        size="sm"
                        variant="outline"
                    >
                        Test Browser Notification
                    </Button>
                </div>

                {/* API Notifications */}
                <div className="border rounded p-4">
                    <h4 className="font-medium mb-2">API Notifications</h4>
                    <p className="text-sm text-gray-600 mb-2">
                        Test sending notifications through the backend API
                    </p>
                    <Button
                        onClick={testAPINotification}
                        className="mt-2"
                        size="sm"
                        variant="outline"
                    >
                        Test API Notification
                    </Button>
                </div>

                {/* Test Results */}
                <div className="border rounded p-4">
                    <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">Test Results</h4>
                        <Button
                            onClick={clearResults}
                            size="sm"
                            variant="ghost"
                        >
                            Clear
                        </Button>
                    </div>
                    <div className="bg-gray-50 rounded p-3 max-h-40 overflow-y-auto">
                        {testResults.length === 0 ? (
                            <p className="text-sm text-gray-500">No test results yet</p>
                        ) : (
                            testResults.map((result, index) => (
                                <div key={index} className="text-xs font-mono mb-1">
                                    {result}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}