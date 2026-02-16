// =============================================================================
// Complete Profile Page
// For new OAuth users to complete their profile information
// =============================================================================

import { useState, useEffect } from 'preact/hooks';
import { route } from 'preact-router';
import { Button } from '../../components/atoms/Button/Button';
import { Icon } from '../../components/atoms/Icon/Icon';
import { BackgroundGradientAnimation } from '../../components/atoms/BackgroundGradientAnimation/BackgroundGradientAnimation';
import { APP_CONFIG, API_CONFIG } from '../../config';

interface ProfileFormData {
    preferred_language?: string;
    district?: string;
    phone?: string;
    specialties?: string;
    experience_years?: number;
}

export function CompleteProfilePage() {
    const [userType, setUserType] = useState<'user' | 'lawyer'>('user');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState<ProfileFormData>({
        preferred_language: 'en',
        district: '',
        phone: '',
        specialties: '',
        experience_years: 0,
    });

    useEffect(() => {
        // Get user type from URL or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const type = urlParams.get('type') || localStorage.getItem(APP_CONFIG.USER_TYPE_STORAGE_KEY) || 'user';
        setUserType(type as 'user' | 'lawyer');
    }, []);

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
            if (!token) {
                throw new Error('No authentication token found');
            }

            const endpoint = userType === 'lawyer'
                ? API_CONFIG.ENDPOINTS.GOOGLE_AUTH.COMPLETE_PROFILE_LAWYER
                : API_CONFIG.ENDPOINTS.GOOGLE_AUTH.COMPLETE_PROFILE_USER;

            const payload = userType === 'lawyer'
                ? {
                    phone: formData.phone,
                    specialties: formData.specialties,
                    experience_years: Number(formData.experience_years),
                    district: formData.district,
                    preferred_language: formData.preferred_language,
                }
                : {
                    preferred_language: formData.preferred_language,
                    district: formData.district,
                };

            const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to complete profile');
            }

            // Profile completed successfully, redirect to dashboard
            setTimeout(() => {
                route('/dashboard');
            }, 500);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to complete profile';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const sriLankanDistricts = [
        'Colombo', 'Gampaha', 'Kalutara', 'Kandy', 'Matale', 'Nuwara Eliya',
        'Galle', 'Matara', 'Hambantota', 'Jaffna', 'Kilinochchi', 'Mannar',
        'Vavuniya', 'Mullaitivu', 'Batticaloa', 'Ampara', 'Trincomalee',
        'Kurunegala', 'Puttalam', 'Anuradhapura', 'Polonnaruwa', 'Badulla',
        'Monaragala', 'Ratnapura', 'Kegalle'
    ];

    return (
        <div className="relative min-h-screen overflow-hidden flex items-center justify-center py-12">
            {/* Background Animation */}
            <div className="absolute inset-0">
                <BackgroundGradientAnimation />
            </div>

            {/* Content */}
            <div className="relative z-10 w-full max-w-2xl mx-auto px-6">
                <div className="bg-card/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-border/50">
                    <div className="text-center mb-8">
                        <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                            <Icon name={userType === 'lawyer' ? 'Briefcase' : 'User'} className="text-primary h-8 w-8" />
                        </div>
                        <h1 className="text-3xl font-bold text-foreground mb-2">
                            Complete Your Profile
                        </h1>
                        <p className="text-muted-foreground">
                            Just a few more details to get started
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-lg bg-destructive/10 border border-destructive/20">
                            <div className="flex items-start gap-3">
                                <Icon name="AlertCircle" className="text-destructive mt-0.5" size="sm" />
                                <p className="text-sm text-destructive">{error}</p>
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Language Preference */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                Preferred Language *
                            </label>
                            <select
                                className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                value={formData.preferred_language}
                                onChange={(e) => setFormData({ ...formData, preferred_language: (e.target as HTMLSelectElement).value })}
                                required
                            >
                                <option value="en">English</option>
                                <option value="si">Sinhala</option>
                                <option value="ta">Tamil</option>
                            </select>
                        </div>

                        {/* District */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                District *
                            </label>
                            <select
                                className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                value={formData.district}
                                onChange={(e) => setFormData({ ...formData, district: (e.target as HTMLSelectElement).value })}
                                required
                            >
                                <option value="">Select your district</option>
                                {sriLankanDistricts.map((district) => (
                                    <option key={district} value={district}>
                                        {district}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Lawyer-specific fields */}
                        {userType === 'lawyer' && (
                            <>
                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-2">
                                        Phone Number *
                                    </label>
                                    <input
                                        type="tel"
                                        className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                        placeholder="+94 77 123 4567"
                                        value={formData.phone}
                                        onInput={(e) => setFormData({ ...formData, phone: (e.target as HTMLInputElement).value })}
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-2">
                                        Legal Specialties *
                                    </label>
                                    <input
                                        type="text"
                                        className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                        placeholder="e.g., Criminal Law, Civil Rights"
                                        value={formData.specialties}
                                        onInput={(e) => setFormData({ ...formData, specialties: (e.target as HTMLInputElement).value })}
                                        required
                                    />
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        Separate multiple specialties with commas
                                    </p>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-2">
                                        Years of Experience *
                                    </label>
                                    <input
                                        type="number"
                                        className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                        min="0"
                                        max="70"
                                        placeholder="5"
                                        value={formData.experience_years?.toString()}
                                        onInput={(e) => setFormData({ ...formData, experience_years: parseInt((e.target as HTMLInputElement).value) || 0 })}
                                        required
                                    />
                                </div>
                            </>
                        )}

                        <div className="flex gap-4 pt-4">
                            <button
                                type="button"
                                className="flex-1 px-4 py-2 rounded-lg border border-border text-foreground hover:bg-secondary transition-colors disabled:opacity-50"
                                onClick={() => route('/')}
                                disabled={isLoading}
                            >
                                Cancel
                            </button>
                            <Button
                                variant="primary"
                                className="flex-1"
                                isLoading={isLoading}
                                disabled={isLoading}
                            >
                                Complete Profile
                            </Button>
                        </div>
                    </form>

                    {userType === 'lawyer' && (
                        <div className="mt-6 p-4 rounded-lg bg-muted/20 border border-border/50">
                            <div className="flex gap-3">
                                <Icon name="Info" className="text-primary mt-0.5 flex-shrink-0" size="sm" />
                                <p className="text-xs text-muted-foreground">
                                    Your profile will be reviewed by our team before activation. 
                                    You'll receive an email once the verification is complete.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
