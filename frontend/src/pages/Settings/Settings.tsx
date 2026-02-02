// =============================================================================
// Settings Page
// User account settings with profile editing, password change, MFA, and sessions
// =============================================================================

import { useState, useEffect } from 'preact/hooks';
import { route } from 'preact-router';
import { useAuth } from '../../hooks/useAuth';
import { BackgroundGradientAnimation } from '../../components/atoms/BackgroundGradientAnimation/BackgroundGradientAnimation';
import { Button } from '../../components/atoms/Button/Button';
import { Input } from '../../components/atoms/Input/Input';
import { Icon } from '../../components/atoms/Icon/Icon';
import { authService } from '../../services/auth';

type SettingsTab = 'profile' | 'security' | 'sessions' | 'preferences';

interface MFAStatus {
    mfa_enabled: boolean;
    mfa_enabled_at: string | null;
    backup_codes_remaining: number;
}

interface Session {
    id: number;
    device_info: string;
    ip_address: string;
    last_activity: string;
    created_at: string;
}

export function Settings() {
    const { user, refreshAuth } = useAuth();
    const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    // Profile form state
    const [profileData, setProfileData] = useState({
        first_name: user?.first_name || '',
        last_name: user?.last_name || '',
        email: user?.email || '',
        district: user?.district || '',
        preferred_language: user?.preferred_language || 'en',
    });

    // Password change state
    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: '',
    });

    // MFA state
    const [mfaStatus, setMfaStatus] = useState<MFAStatus | null>(null);
    const [mfaSetup, setMfaSetup] = useState<{
        secret: string;
        qr_code_url: string;
        backup_codes: string[];
    } | null>(null);
    const [mfaCode, setMfaCode] = useState('');
    const [disablePassword, setDisablePassword] = useState('');

    // Sessions state
    const [sessions, setSessions] = useState<Session[]>([]);

    useEffect(() => {
        if (user) {
            setProfileData({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                email: user.email || '',
                district: user.district || '',
                preferred_language: user.preferred_language || 'en',
            });
        }
    }, [user]);

    useEffect(() => {
        if (activeTab === 'security') {
            loadMFAStatus();
        } else if (activeTab === 'sessions') {
            loadSessions();
        }
    }, [activeTab]);

    const showMessage = (type: 'success' | 'error', text: string) => {
        setMessage({ type, text });
        setTimeout(() => setMessage(null), 5000);
    };

    // Copy to clipboard helper
    const copyToClipboard = async (text: string, label: string) => {
        try {
            await navigator.clipboard.writeText(text);
            showMessage('success', `${label} copied to clipboard!`);
        } catch (error) {
            showMessage('error', 'Failed to copy to clipboard');
        }
    };

    // Profile update handler
    const handleProfileUpdate = async (e: Event) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            await authService.updateProfile(profileData);
            await refreshAuth();
            showMessage('success', 'Profile updated successfully');
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to update profile');
        } finally {
            setIsLoading(false);
        }
    };

    // Password change handler
    const handlePasswordChange = async (e: Event) => {
        e.preventDefault();

        if (passwordData.new_password !== passwordData.confirm_password) {
            showMessage('error', 'New passwords do not match');
            return;
        }

        setIsLoading(true);

        try {
            await authService.changePassword(
                passwordData.current_password,
                passwordData.new_password
            );
            setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
            showMessage('success', 'Password changed successfully');
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to change password');
        } finally {
            setIsLoading(false);
        }
    };

    // MFA handlers
    const loadMFAStatus = async () => {
        try {
            const status = await authService.getMFAStatus();
            setMfaStatus(status);
        } catch (error) {
            console.error('Failed to load MFA status:', error);
        }
    };

    const handleSetupMFA = async () => {
        setIsLoading(true);
        try {
            const setup = await authService.setupMFA();
            setMfaSetup(setup);
            showMessage('success', 'Scan the QR code with your authenticator app');
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to setup MFA');
        } finally {
            setIsLoading(false);
        }
    };

    const handleEnableMFA = async (e: Event) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            await authService.enableMFA(mfaCode);
            setMfaSetup(null);
            setMfaCode('');
            await loadMFAStatus();
            showMessage('success', 'MFA enabled successfully');
        } catch (error: any) {
            showMessage('error', error.message || 'Invalid verification code');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDisableMFA = async (e: Event) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            await authService.disableMFA(disablePassword);
            setDisablePassword('');
            await loadMFAStatus();
            showMessage('success', 'MFA disabled successfully');
        } catch (error: any) {
            showMessage('error', error.message || 'Invalid password');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegenerateBackupCodes = async () => {
        setIsLoading(true);
        try {
            const codes = await authService.regenerateBackupCodes();
            setMfaSetup(codes);
            showMessage('success', 'Backup codes regenerated. Save them securely!');
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to regenerate backup codes');
        } finally {
            setIsLoading(false);
        }
    };

    // Sessions handlers
    const loadSessions = async () => {
        try {
            const data = await authService.getActiveSessions();
            setSessions(data.sessions);
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    };

    const handleRevokeSession = async (sessionId: number) => {
        if (!confirm('Are you sure you want to revoke this session?')) return;

        try {
            await authService.revokeSession(sessionId);
            await loadSessions();
            showMessage('success', 'Session revoked successfully');
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to revoke session');
        }
    };

    const tabs = [
        { id: 'profile' as SettingsTab, label: 'Profile', icon: 'User' },
        { id: 'security' as SettingsTab, label: 'Security', icon: 'Shield' },
        { id: 'sessions' as SettingsTab, label: 'Sessions', icon: 'Monitor' },
        { id: 'preferences' as SettingsTab, label: 'Preferences', icon: 'Settings' },
    ];

    return (
        <div className="min-h-screen relative">
            {/* Background with gradient - fixed to always cover viewport */}
            <div className="fixed inset-0 z-0">
                <BackgroundGradientAnimation />
            </div>

            {/* Settings content */}
            <div className="relative z-10 min-h-screen p-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="mb-8 flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
                            <p className="text-white/70">Manage your account settings and preferences</p>
                        </div>
                        <Button variant="ghost" onClick={() => route('/dashboard')}>
                            <Icon name="X" size="sm" className="mr-2" />
                            Close
                        </Button>
                    </div>

                    {/* Message banner */}
                    {message && (
                        <div
                            className={`mb-6 p-4 rounded-lg ${message.type === 'success'
                                ? 'bg-green-500/20 border border-green-500/50 text-green-100'
                                : 'bg-red-500/20 border border-red-500/50 text-red-100'
                                }`}
                        >
                            <div className="flex items-center gap-2">
                                <Icon
                                    name={message.type === 'success' ? 'CheckCircle' : 'AlertCircle'}
                                    size="sm"
                                />
                                <span>{message.text}</span>
                            </div>
                        </div>
                    )}

                    {/* Tabs */}
                    <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${activeTab === tab.id
                                    ? 'bg-white/20 text-white border border-white/30'
                                    : 'bg-white/5 text-white/70 hover:bg-white/10 border border-white/10'
                                    }`}
                            >
                                <Icon name={tab.icon as any} size="sm" />
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Tab content */}
                    <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-8">
                        {/* Profile Tab */}
                        {activeTab === 'profile' && (
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-6">Profile Information</h2>

                                {/* Email Verification Notice */}
                                {user && !user.email_verified && (
                                    <div className="mb-6 bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4">
                                        <div className="flex items-start gap-3">
                                            <Icon name="AlertCircle" className="text-yellow-400 mt-0.5" />
                                            <div className="flex-1">
                                                <h3 className="text-yellow-100 font-semibold mb-1">
                                                    Email Not Verified
                                                </h3>
                                                <p className="text-yellow-100/80 text-sm mb-3">
                                                    Please verify your email address to access all features. Check your inbox for the verification link.
                                                </p>
                                                <Button
                                                    variant="secondary"
                                                    size="sm"
                                                    onClick={async () => {
                                                        setIsLoading(true);
                                                        try {
                                                            await authService.resendVerificationEmail();
                                                            showMessage('success', 'Verification email sent! Please check your inbox.');
                                                        } catch (error: any) {
                                                            showMessage('error', error.message || 'Failed to send verification email');
                                                        } finally {
                                                            setIsLoading(false);
                                                        }
                                                    }}
                                                    isLoading={isLoading}
                                                >
                                                    <Icon name="Mail" size="sm" className="mr-2" />
                                                    Resend Verification Email
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <form onSubmit={handleProfileUpdate} className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                First Name
                                            </label>
                                            <Input
                                                type="text"
                                                value={profileData.first_name}
                                                onChange={(e) =>
                                                    setProfileData({
                                                        ...profileData,
                                                        first_name: (e.target as HTMLInputElement).value,
                                                    })
                                                }
                                                className="bg-white/10 border-white/20 text-white"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                Last Name
                                            </label>
                                            <Input
                                                type="text"
                                                value={profileData.last_name}
                                                onChange={(e) =>
                                                    setProfileData({
                                                        ...profileData,
                                                        last_name: (e.target as HTMLInputElement).value,
                                                    })
                                                }
                                                className="bg-white/10 border-white/20 text-white"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-white/80 mb-2">
                                            Email Address
                                        </label>
                                        <Input
                                            type="email"
                                            value={profileData.email}
                                            className="bg-white/5 border-white/20 text-white/50 cursor-not-allowed"
                                        />
                                        <p className="text-xs text-white/50 mt-1">
                                            Email cannot be changed
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                District
                                            </label>
                                            <Input
                                                type="text"
                                                value={profileData.district}
                                                onChange={(e) =>
                                                    setProfileData({
                                                        ...profileData,
                                                        district: (e.target as HTMLInputElement).value,
                                                    })
                                                }
                                                className="bg-white/10 border-white/20 text-white"
                                                placeholder="Enter your district"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                Preferred Language
                                            </label>
                                            <select
                                                value={profileData.preferred_language}
                                                onChange={(e) =>
                                                    setProfileData({
                                                        ...profileData,
                                                        preferred_language: (e.target as HTMLSelectElement).value,
                                                    })
                                                }
                                                className="w-full px-4 py-2 bg-white/10 border border-white/20 text-white rounded-lg"
                                            >
                                                <option value="en" className="bg-gray-800">English</option>
                                                <option value="si" className="bg-gray-800">Sinhala</option>
                                                <option value="ta" className="bg-gray-800">Tamil</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div className="flex justify-end">
                                        <Button onClick={handleProfileUpdate as any} isLoading={isLoading}>
                                            <Icon name="Save" size="sm" className="mr-2" />
                                            Save Changes
                                        </Button>
                                    </div>
                                </form>
                            </div>
                        )}

                        {/* Security Tab */}
                        {activeTab === 'security' && (
                            <div className="space-y-8">
                                {/* Password Change */}
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-6">Change Password</h2>
                                    <form onSubmit={handlePasswordChange} className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                Current Password
                                            </label>
                                            <Input
                                                type="password"
                                                value={passwordData.current_password}
                                                onChange={(e) =>
                                                    setPasswordData({
                                                        ...passwordData,
                                                        current_password: (e.target as HTMLInputElement).value,
                                                    })
                                                }
                                                className="bg-white/10 border-white/20 text-white"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                New Password
                                            </label>
                                            <Input
                                                type="password"
                                                value={passwordData.new_password}
                                                onChange={(e) =>
                                                    setPasswordData({
                                                        ...passwordData,
                                                        new_password: (e.target as HTMLInputElement).value,
                                                    })
                                                }
                                                className="bg-white/10 border-white/20 text-white"
                                            />
                                            <p className="text-xs text-white/50 mt-1">
                                                Must be at least 8 characters with uppercase, lowercase, number, and
                                                special character
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-white/80 mb-2">
                                                Confirm New Password
                                            </label>
                                            <Input
                                                type="password"
                                                value={passwordData.confirm_password}
                                                onChange={(e) =>
                                                    setPasswordData({
                                                        ...passwordData,
                                                        confirm_password: (e.target as HTMLInputElement).value,
                                                    })
                                                }
                                                className="bg-white/10 border-white/20 text-white"
                                            />
                                        </div>
                                        <div className="flex justify-end">
                                            <Button onClick={handlePasswordChange as any} isLoading={isLoading}>
                                                <Icon name="Key" size="sm" className="mr-2" />
                                                Change Password
                                            </Button>
                                        </div>
                                    </form>
                                </div>

                                <div className="border-t border-white/20 pt-8">
                                    {/* MFA Section */}
                                    <h2 className="text-2xl font-bold text-white mb-6">
                                        Two-Factor Authentication (MFA)
                                    </h2>

                                    {mfaStatus && !mfaStatus.mfa_enabled && !mfaSetup && (
                                        <div className="bg-white/5 border border-white/20 rounded-lg p-6">
                                            <div className="flex items-start gap-4">
                                                <Icon name="Shield" className="text-blue-400 mt-1" />
                                                <div className="flex-1">
                                                    <h3 className="text-lg font-semibold text-white mb-2">
                                                        Enhance Your Account Security
                                                    </h3>
                                                    <p className="text-white/70 mb-4">
                                                        Enable two-factor authentication to add an extra layer of
                                                        security to your account.
                                                    </p>
                                                    <Button onClick={handleSetupMFA} isLoading={isLoading}>
                                                        <Icon name="ShieldCheck" size="sm" className="mr-2" />
                                                        Enable MFA
                                                    </Button>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {mfaSetup && (
                                        <div className="bg-white/5 border border-white/20 rounded-lg p-6 space-y-6">
                                            <div>
                                                <h3 className="text-lg font-semibold text-white mb-4">
                                                    Step 1: Scan QR Code
                                                </h3>
                                                <p className="text-white/70 mb-4">
                                                    Scan this QR code with your authenticator app (Google
                                                    Authenticator, Authy, etc.)
                                                </p>
                                                <div className="bg-white p-4 rounded-lg inline-block">
                                                    <img
                                                        src={mfaSetup.qr_code_url}
                                                        alt="MFA QR Code"
                                                        className="w-48 h-48"
                                                    />
                                                </div>
                                                <p className="text-sm text-white/50 mt-2">
                                                    Or enter this code manually: <code className="bg-white/10 px-2 py-1 rounded">{mfaSetup.secret}</code>
                                                </p>
                                            </div>

                                            <div>
                                                <h3 className="text-lg font-semibold text-white mb-4">
                                                    Step 2: Save Backup Codes
                                                </h3>
                                                <p className="text-white/70 mb-4">
                                                    Save these backup codes in a secure place. You can use them to
                                                    access your account if you lose your device.
                                                </p>
                                                <div className="bg-black/30 p-4 rounded-lg">
                                                    <div className="grid grid-cols-2 gap-2 mb-4">
                                                        {mfaSetup.backup_codes.map((code, index) => (
                                                            <code key={index} className="text-white/90 text-sm">
                                                                {code}
                                                            </code>
                                                        ))}
                                                    </div>
                                                    <Button
                                                        variant="secondary"
                                                        size="sm"
                                                        onClick={() => copyToClipboard(mfaSetup.backup_codes.join('\n'), 'Backup codes')}
                                                    >
                                                        <Icon name="Copy" size="sm" className="mr-2" />
                                                        Copy All Codes
                                                    </Button>
                                                </div>
                                            </div>

                                            <div>
                                                <h3 className="text-lg font-semibold text-white mb-4">
                                                    Step 3: Verify Setup
                                                </h3>
                                                <form onSubmit={handleEnableMFA} className="space-y-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-white/80 mb-2">
                                                            Enter 6-digit code from your authenticator app
                                                        </label>
                                                        <input
                                                            type="text"
                                                            value={mfaCode}
                                                            onChange={(e) =>
                                                                setMfaCode((e.target as HTMLInputElement).value)
                                                            }
                                                            placeholder="000000"
                                                            maxLength={6}
                                                            className="w-full px-4 py-2 bg-white/10 border border-white/20 text-white rounded-lg"
                                                        />
                                                    </div>
                                                    <div className="flex gap-2">
                                                        <Button onClick={handleEnableMFA as any} isLoading={isLoading}>
                                                            <Icon name="Check" size="sm" className="mr-2" />
                                                            Verify and Enable
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            onClick={() => setMfaSetup(null)}
                                                        >
                                                            Cancel
                                                        </Button>
                                                    </div>
                                                </form>
                                            </div>
                                        </div>
                                    )}

                                    {mfaStatus && mfaStatus.mfa_enabled && (
                                        <div className="bg-white/5 border border-green-500/30 rounded-lg p-6 space-y-6">
                                            <div className="flex items-center gap-3">
                                                <Icon name="ShieldCheck" className="text-green-400" />
                                                <div>
                                                    <h3 className="text-lg font-semibold text-white">
                                                        MFA is Enabled
                                                    </h3>
                                                    <p className="text-white/70 text-sm">
                                                        Your account is protected with two-factor authentication
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="text-white/70 text-sm">
                                                <p>
                                                    Enabled on:{' '}
                                                    {mfaStatus.mfa_enabled_at
                                                        ? new Date(mfaStatus.mfa_enabled_at).toLocaleDateString()
                                                        : 'Unknown'}
                                                </p>
                                                <p>Backup codes remaining: {mfaStatus.backup_codes_remaining}</p>
                                            </div>

                                            <div className="flex gap-2">
                                                <Button
                                                    variant="secondary"
                                                    onClick={handleRegenerateBackupCodes}
                                                    isLoading={isLoading}
                                                >
                                                    <Icon name="RefreshCw" size="sm" className="mr-2" />
                                                    Regenerate Backup Codes
                                                </Button>
                                            </div>

                                            <div className="border-t border-white/20 pt-4">
                                                <h4 className="text-white font-medium mb-3">Disable MFA</h4>
                                                <form onSubmit={handleDisableMFA} className="space-y-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-white/80 mb-2">
                                                            Enter your password to disable MFA
                                                        </label>
                                                        <Input
                                                            type="password"
                                                            value={disablePassword}
                                                            onChange={(e) =>
                                                                setDisablePassword(
                                                                    (e.target as HTMLInputElement).value
                                                                )
                                                            }
                                                            className="bg-white/10 border-white/20 text-white"
                                                        />
                                                    </div>
                                                    <Button
                                                        onClick={handleDisableMFA as any}
                                                        variant="destructive"
                                                        isLoading={isLoading}
                                                    >
                                                        <Icon name="ShieldOff" size="sm" className="mr-2" />
                                                        Disable MFA
                                                    </Button>
                                                </form>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Sessions Tab */}
                        {activeTab === 'sessions' && (
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-6">Active Sessions</h2>
                                <p className="text-white/70 mb-6">
                                    Manage your active sessions. You can revoke access to any session if you don't
                                    recognize it.
                                </p>

                                {sessions.length === 0 ? (
                                    <div className="text-center py-12 text-white/50">
                                        <Icon name="Monitor" className="mx-auto mb-4" size="lg" />
                                        <p>No active sessions found</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {sessions.map((session) => (
                                            <div
                                                key={session.id}
                                                className="bg-white/5 border border-white/20 rounded-lg p-4 flex items-center justify-between"
                                            >
                                                <div className="flex items-start gap-4">
                                                    <Icon name="Monitor" className="text-blue-400 mt-1" />
                                                    <div>
                                                        <h3 className="text-white font-medium">
                                                            {session.device_info || 'Unknown Device'}
                                                        </h3>
                                                        <p className="text-white/70 text-sm">
                                                            IP: {session.ip_address}
                                                        </p>
                                                        <p className="text-white/50 text-xs mt-1">
                                                            Last active:{' '}
                                                            {new Date(session.last_activity).toLocaleString()}
                                                        </p>
                                                        <p className="text-white/50 text-xs">
                                                            Created: {new Date(session.created_at).toLocaleString()}
                                                        </p>
                                                    </div>
                                                </div>
                                                <Button
                                                    variant="destructive"
                                                    size="sm"
                                                    onClick={() => handleRevokeSession(session.id)}
                                                >
                                                    <Icon name="Trash2" size="sm" className="mr-2" />
                                                    Revoke
                                                </Button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Preferences Tab */}
                        {activeTab === 'preferences' && (
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-6">Preferences</h2>
                                <div className="bg-white/5 border border-white/20 rounded-lg p-6">
                                    <p className="text-white/70">
                                        Additional preferences will be available here soon.
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Settings;
