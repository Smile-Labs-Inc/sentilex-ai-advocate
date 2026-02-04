// =============================================================================
// Authentication Page
// Login and Register forms for users and lawyers
// =============================================================================

import { useState } from 'preact/hooks';
import { Button } from '../../components/atoms/Button/Button';
import { Input } from '../../components/atoms/Input/Input';
import { Icon } from '../../components/atoms/Icon/Icon';
import { BackgroundGradientAnimation } from '../../components/atoms/BackgroundGradientAnimation/BackgroundGradientAnimation';
import { useAuth } from '../../hooks/useAuth';
import { APP_CONFIG, API_CONFIG } from '../../config';
import type { UserType } from '../../types/auth';

type AuthMode = 'login' | 'register' | 'forgot-password';

interface AuthPageProps {
    onSuccess?: () => void;
}

export function AuthPage({ onSuccess }: AuthPageProps) {
    const { login, register } = useAuth();
    const [mode, setMode] = useState<AuthMode>('login');
    const [userType, setUserType] = useState<UserType>('user');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Login form state
    const [loginEmail, setLoginEmail] = useState('');
    const [loginPassword, setLoginPassword] = useState('');

    // Forgot password state
    const [forgotPasswordEmail, setForgotPasswordEmail] = useState('');

    // Register form state
    const [registerData, setRegisterData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        confirmPassword: '',
        preferred_language: 'en',
        district: '',
    });

    const handleLogin = async (e: Event) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setIsLoading(true);

        try {
            await login({
                email: loginEmail,
                password: loginPassword,
            });

            setSuccess('Login successful!');

            // Call onSuccess callback if provided
            setTimeout(() => {
                onSuccess?.();
            }, 500);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Login failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegister = async (e: Event) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        // Validate passwords match
        if (registerData.password !== registerData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setIsLoading(true);

        try {
            const { confirmPassword, ...registrationData } = registerData;
            const response = await register(registrationData);

            setSuccess(response.message);

            // Switch to login mode after successful registration
            setTimeout(() => {
                setMode('login');
                setLoginEmail(registerData.email);
            }, 2000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Registration failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleForgotPassword = async (e: Event) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setIsLoading(true);

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.FORGOT_PASSWORD}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: forgotPasswordEmail }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Password reset request failed');
            }

            setSuccess('Password reset link has been sent to your email');
            setTimeout(() => {
                setMode('login');
                setForgotPasswordEmail('');
            }, 3000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send reset email');
        } finally {
            setIsLoading(false);
        }
    };

    const handleGoogleLogin = () => {
        const googleLoginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GOOGLE_AUTH.LOGIN}?user_type=${userType}`;
        window.location.href = googleLoginUrl;
    };

    return (
        <div className="relative h-screen overflow-hidden flex">
            {/* Background Animation - Full Screen */}
            <div className="absolute inset-0">
                <BackgroundGradientAnimation />
            </div>

            {/* Left Side - Branding */}
            <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
                <div className="relative z-10 flex flex-col items-center justify-center h-full w-full p-12 text-center">
                    <h1 className="text-6xl font-bold text-white mb-6">
                        {APP_CONFIG.NAME}
                    </h1>
                    <p className="text-2xl text-white/90 max-w-lg leading-relaxed">
                        Your AI-powered legal advocate for digital rights and justice
                    </p>
                </div>
            </div>

            {/* Right Side - Auth Form */}
            <div className="w-full lg:w-1/2 relative flex items-center justify-center p-3 overflow-y-auto">
                <div className="w-full max-w-md">
                    {/* Mobile Header */}
                    <div className="text-center mb-3 lg:hidden">
                        <h1 className="text-lg font-bold text-white mb-0.5">
                            {APP_CONFIG.NAME}
                        </h1>
                    </div>

                    {/* Auth Card Content */}
                    <div className="space-y-3">
                        {/* Header */}
                        <div className="text-center">
                            <h2 className="text-lg font-bold text-foreground mb-1">
                                {mode === 'login' ? 'Welcome Back' : 'Get Started'}
                            </h2>
                            <p className="text-xs text-muted-foreground">
                                {mode === 'login' ? 'Sign in to your account' : 'Create your account'}
                            </p>
                        </div>

                        {/* User Type Toggle */}
                        <div className="flex gap-1 p-0.5 bg-secondary rounded-lg">
                            <button
                                onClick={() => setUserType('user')}
                                className={`flex-1 py-1 px-1.5 rounded-md text-xs font-medium transition-all ${userType === 'user'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                <Icon name="User" className="inline-block w-3 h-3 mr-0.5" />
                                User
                            </button>
                            <button
                                onClick={() => setUserType('lawyer')}
                                className={`flex-1 py-1 px-1.5 rounded-md text-xs font-medium transition-all ${userType === 'lawyer'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                <Icon name="Briefcase" className="inline-block w-3 h-3 mr-0.5" />
                                Lawyer
                            </button>
                        </div>

                        {/* Error/Success Messages */}
                        {error && (
                            <div className="p-1.5 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs">
                                {error}
                            </div>
                        )}
                        {success && (
                            <div className="p-1.5 rounded-lg bg-green-500/10 border border-green-500/20 text-green-500 text-xs">
                                {success}
                            </div>
                        )}

                        {/* Login Form */}
                        {mode === 'login' && (
                            <form onSubmit={handleLogin} className="space-y-2.5">
                                <div>
                                    <label className="block text-xs font-medium text-foreground mb-1">
                                        Email
                                    </label>
                                    <Input
                                        type="email"
                                        placeholder="your@email.com"
                                        value={loginEmail}
                                        onInput={(e) => setLoginEmail((e.target as HTMLInputElement).value)}
                                    />
                                </div>

                                <div>
                                    <div className="flex items-center justify-between mb-1">
                                        <label className="block text-xs font-medium text-foreground">
                                            Password
                                        </label>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setMode('forgot-password');
                                                setError(null);
                                                setSuccess(null);
                                            }}
                                            className="text-xs text-primary hover:text-primary/80 transition-colors"
                                        >
                                            Forgot?
                                        </button>
                                    </div>
                                    <Input
                                        type="password"
                                        placeholder="••••••••"
                                        value={loginPassword}
                                        onInput={(e) => setLoginPassword((e.target as HTMLInputElement).value)}
                                    />
                                </div>

                                <Button
                                    variant="primary"
                                    className="w-full text-xs py-1.5 mt-1"
                                    isLoading={isLoading}
                                    disabled={isLoading}
                                >
                                    Sign In
                                </Button>
                            </form>
                        )}

                        {/* Register Form */}
                        {mode === 'register' && (
                            <form onSubmit={handleRegister} className="space-y-2">
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1">
                                            First Name
                                        </label>
                                        <Input
                                            type="text"
                                            placeholder="John"
                                            value={registerData.first_name}
                                            onInput={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    first_name: (e.target as HTMLInputElement).value,
                                                })
                                            }
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1">
                                            Last Name
                                        </label>
                                        <Input
                                            type="text"
                                            placeholder="Doe"
                                            value={registerData.last_name}
                                            onInput={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    last_name: (e.target as HTMLInputElement).value,
                                                })
                                            }
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-foreground mb-1">
                                        Email
                                    </label>
                                    <Input
                                        type="email"
                                        placeholder="your@email.com"
                                        value={registerData.email}
                                        onInput={(e) =>
                                            setRegisterData({
                                                ...registerData,
                                                email: (e.target as HTMLInputElement).value,
                                            })
                                        }
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-foreground mb-1">
                                        District (Optional)
                                    </label>
                                    <Input
                                        type="text"
                                        placeholder="Colombo"
                                        value={registerData.district}
                                        onInput={(e) =>
                                            setRegisterData({
                                                ...registerData,
                                                district: (e.target as HTMLInputElement).value,
                                            })
                                        }
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1">
                                            Password
                                        </label>
                                        <Input
                                            type="password"
                                            placeholder="••••••••"
                                            value={registerData.password}
                                            onInput={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    password: (e.target as HTMLInputElement).value,
                                                })
                                            }
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1">
                                            Confirm
                                        </label>
                                        <Input
                                            type="password"
                                            placeholder="••••••••"
                                            value={registerData.confirmPassword}
                                            onInput={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    confirmPassword: (e.target as HTMLInputElement).value,
                                                })
                                            }
                                        />
                                    </div>
                                </div>

                                <Button
                                    variant="primary"
                                    className="w-full text-xs py-1.5 mt-1"
                                    isLoading={isLoading}
                                    disabled={isLoading}
                                >
                                    Create Account
                                </Button>
                            </form>
                        )}

                        {/* Forgot Password Form */}
                        {mode === 'forgot-password' && (
                            <form onSubmit={handleForgotPassword} className="space-y-2">
                                <div>
                                    <label className="block text-xs font-medium text-foreground mb-0.5">
                                        Email Address
                                    </label>
                                    <Input
                                        type="email"
                                        placeholder="your@email.com"
                                        value={forgotPasswordEmail}
                                        onInput={(e) => setForgotPasswordEmail((e.target as HTMLInputElement).value)}
                                    />
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        We'll send you a link to reset your password
                                    </p>
                                </div>

                                <Button
                                    variant="primary"
                                    className="w-full text-xs py-1"
                                    isLoading={isLoading}
                                    disabled={isLoading}
                                >
                                    Send Reset Link
                                </Button>

                                <button
                                    type="button"
                                    onClick={() => {
                                        setMode('login');
                                        setError(null);
                                        setSuccess(null);
                                    }}
                                    className="w-full text-xs text-muted-foreground hover:text-foreground transition-colors"
                                    disabled={isLoading}
                                >
                                    Back to login
                                </button>
                            </form>
                        )}

                        {/* Google OAuth */}
                        {APP_CONFIG.GOOGLE_AUTH_ENABLED && (
                            <>
                                <div className="relative my-2">
                                    <div className="absolute inset-0 flex items-center">
                                        <div className="w-full border-t border-border"></div>
                                    </div>
                                    <div className="relative flex justify-center text-xs">
                                        <span className="px-2 bg-background text-muted-foreground">Or continue with</span>
                                    </div>
                                </div>

                                <Button
                                    variant="outline"
                                    className="w-full text-xs py-1"
                                    onClick={handleGoogleLogin}
                                    disabled={isLoading}
                                >
                                    <Icon name="Chrome" className="w-3 h-3 mr-1" />
                                    Google
                                </Button>
                            </>
                        )}

                        {/* Mode Toggle */}
                        <div className="text-center">
                            <button
                                onClick={() => {
                                    setMode(mode === 'login' ? 'register' : 'login');
                                    setError(null);
                                    setSuccess(null);
                                }}
                                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                                disabled={isLoading}
                            >
                                {mode === 'login' ? (
                                    <>
                                        Don't have an account?{' '}
                                        <span className="text-primary font-medium">Sign up</span>
                                    </>
                                ) : (
                                    <>
                                        Already have an account?{' '}
                                        <span className="text-primary font-medium">Sign in</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
