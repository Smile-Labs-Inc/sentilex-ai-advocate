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
    const { login, register, error: authError, isLoading: authLoading } = useAuth();
    const [mode, setMode] = useState<AuthMode>('login');
    const [userType, setUserType] = useState<UserType>('user');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Use auth error from context if available, otherwise use local error
    const displayError = authError || error;

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

    // Password validation state
    const [passwordValidation, setPasswordValidation] = useState({
        minLength: false,
        hasUppercase: false,
        hasLowercase: false,
        hasDigit: false,
        hasSpecial: false,
        passwordsMatch: true,
    });

    // Validate password in real-time
    const validatePassword = (password: string, confirmPassword: string) => {
        setPasswordValidation({
            minLength: password.length >= 8,
            hasUppercase: /[A-Z]/.test(password),
            hasLowercase: /[a-z]/.test(password),
            hasDigit: /\d/.test(password),
            hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
            passwordsMatch: !confirmPassword || password === confirmPassword,
        });
    };

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
            const errorMessage = err instanceof Error ? err.message : 'Login failed';

            // Add user-friendly context to common errors
            let displayError = errorMessage;
            if (errorMessage.includes('Incorrect email or password')) {
                displayError = 'Incorrect email or password. Please check your credentials and try again.';
            } else if (errorMessage.includes('Account is inactive')) {
                displayError = 'Your account is inactive. Please contact support.';
            } else if (errorMessage.includes('email_verified')) {
                displayError = 'Please verify your email address before logging in. Check your inbox for the verification link.';
            }

            setError(displayError);
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

            // Show detailed success message
            const successMsg = response.verification_sent
                ? `${response.message} Please check your email to verify your account.`
                : response.message;
            setSuccess(successMsg);

            // Switch to login mode after successful registration
            setTimeout(() => {
                setMode('login');
                setLoginEmail(registerData.email);
                setSuccess('Email verified! You can now log in.');
                // Clear the second message after showing login form
                setTimeout(() => setSuccess(null), 3000);
            }, 3000);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Registration failed';
            setError(errorMessage);
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
            <div className="w-full lg:w-1/2 relative flex items-center justify-center p-4 overflow-y-auto">
                <div className="w-full max-w-xl">
                    {/* Mobile Header */}
                    <div className="text-center mb-3 lg:hidden">
                        <h1 className="text-xl font-bold text-white mb-1">
                            {APP_CONFIG.NAME}
                        </h1>
                    </div>

                    {/* Auth Card Content */}
                    <div className="space-y-3.5">
                        {/* Header */}
                        <div className="text-center">
                            <h2 className="text-xl font-bold text-foreground mb-1.5">
                                {mode === 'login' ? 'Welcome Back' : 'Get Started'}
                            </h2>
                            <p className="text-sm text-muted-foreground">
                                {mode === 'login' ? 'Sign in to your account' : 'Create your account'}
                            </p>
                        </div>

                        {/* User Type Toggle */}
                        <div className="flex gap-1.5 p-1 bg-secondary rounded-lg">
                            <button
                                onClick={() => setUserType('user')}
                                className={`flex-1 py-2 px-2.5 rounded-md text-xs font-medium transition-all ${userType === 'user'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                <Icon name="User" className="inline-block w-3.5 h-3.5 mr-0.5" />
                                User
                            </button>
                            <button
                                onClick={() => setUserType('lawyer')}
                                className={`flex-1 py-2 px-2.5 rounded-md text-xs font-medium transition-all ${userType === 'lawyer'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                <Icon name="Briefcase" className="inline-block w-3.5 h-3.5 mr-0.5" />
                                Lawyer
                            </button>
                        </div>

                        {/* Error/Success Messages */}
                        {displayError && (
                            <div className="p-3 rounded-lg bg-white/5 border border-white/20 backdrop-blur-sm">
                                <div className="flex items-start gap-2.5">
                                    <Icon name="Info" className="text-white/60 mt-0.5 flex-shrink-0" size="sm" />
                                    <div className="flex-1">
                                        {displayError.split('\n').map((line, i) => (
                                            <p key={i} className="text-sm text-white/80 leading-relaxed">{line}</p>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                        {success && (
                            <div className="p-3 rounded-lg bg-white/5 border border-white/20 backdrop-blur-sm">
                                <div className="flex items-start gap-2.5">
                                    <Icon name="CheckCircle" className="text-white/60 mt-0.5 flex-shrink-0" size="sm" />
                                    <p className="text-sm text-white/80 leading-relaxed">{success}</p>
                                </div>
                            </div>
                        )}

                        {/* Login Form */}
                        {mode === 'login' && (
                            <form onSubmit={handleLogin} className="space-y-3">
                                <div>
                                    <label className="block text-xs font-medium text-foreground mb-1.5">
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
                                    <div className="flex items-center justify-between mb-1.5">
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
                                    className="w-full text-xs py-2 mt-1.5"
                                    isLoading={isLoading}
                                    disabled={isLoading}
                                >
                                    Sign In
                                </Button>
                            </form>
                        )}

                        {/* Register Form */}
                        {mode === 'register' && (
                            <form onSubmit={handleRegister} className="space-y-2.5">
                                <div className="grid grid-cols-2 gap-2.5">
                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1.5">
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
                                        <label className="block text-xs font-medium text-foreground mb-1.5">
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
                                    <label className="block text-xs font-medium text-foreground mb-1.5">
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
                                    <label className="block text-xs font-medium text-foreground mb-1.5">
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

                                <div className="grid grid-cols-2 gap-2.5">
                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1.5">
                                            Password
                                        </label>
                                        <Input
                                            type="password"
                                            placeholder="••••••••"
                                            value={registerData.password}
                                            onInput={(e) => {
                                                const newPassword = (e.target as HTMLInputElement).value;
                                                setRegisterData({
                                                    ...registerData,
                                                    password: newPassword,
                                                });
                                                validatePassword(newPassword, registerData.confirmPassword);
                                            }}
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs font-medium text-foreground mb-1.5">
                                            Confirm
                                        </label>
                                        <Input
                                            type="password"
                                            placeholder="••••••••"
                                            value={registerData.confirmPassword}
                                            onInput={(e) => {
                                                const newConfirm = (e.target as HTMLInputElement).value;
                                                setRegisterData({
                                                    ...registerData,
                                                    confirmPassword: newConfirm,
                                                });
                                                validatePassword(registerData.password, newConfirm);
                                            }}
                                        />
                                    </div>
                                </div>
                                {/* Live Password Validation */}
                                {registerData.password && (
                                    <div className="bg-muted/20 border border-border/50 rounded px-2 py-2 -mt-1">
                                        <p className="text-xs font-medium text-foreground/70 mb-1.5">Password must have:</p>
                                        <div className="space-y-0.5">
                                            <div className={`flex items-center gap-1.5 text-xs ${passwordValidation.minLength ? 'text-green-500' : 'text-muted-foreground'
                                                }`}>
                                                <Icon name={passwordValidation.minLength ? 'CheckCircle' : 'Circle'} size="sm" className="w-3 h-3" />
                                                <span>At least 8 characters</span>
                                            </div>
                                            <div className={`flex items-center gap-1.5 text-xs ${passwordValidation.hasUppercase ? 'text-green-500' : 'text-muted-foreground'
                                                }`}>
                                                <Icon name={passwordValidation.hasUppercase ? 'CheckCircle' : 'Circle'} size="sm" className="w-3 h-3" />
                                                <span>One uppercase letter</span>
                                            </div>
                                            <div className={`flex items-center gap-1.5 text-xs ${passwordValidation.hasLowercase ? 'text-green-500' : 'text-muted-foreground'
                                                }`}>
                                                <Icon name={passwordValidation.hasLowercase ? 'CheckCircle' : 'Circle'} size="sm" className="w-3 h-3" />
                                                <span>One lowercase letter</span>
                                            </div>
                                            <div className={`flex items-center gap-1.5 text-xs ${passwordValidation.hasDigit ? 'text-green-500' : 'text-muted-foreground'
                                                }`}>
                                                <Icon name={passwordValidation.hasDigit ? 'CheckCircle' : 'Circle'} size="sm" className="w-3 h-3" />
                                                <span>One digit</span>
                                            </div>
                                            <div className={`flex items-center gap-1.5 text-xs ${passwordValidation.hasSpecial ? 'text-green-500' : 'text-muted-foreground'
                                                }`}>
                                                <Icon name={passwordValidation.hasSpecial ? 'CheckCircle' : 'Circle'} size="sm" className="w-3 h-3" />
                                                <span>One special character (!@#$%...)</span>
                                            </div>
                                            {registerData.confirmPassword && (
                                                <div className={`flex items-center gap-1.5 text-xs ${passwordValidation.passwordsMatch ? 'text-green-500' : 'text-destructive'
                                                    }`}>
                                                    <Icon name={passwordValidation.passwordsMatch ? 'CheckCircle' : 'XCircle'} size="sm" className="w-3 h-3" />
                                                    <span>Passwords match</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                <Button
                                    variant="primary"
                                    className="w-full text-xs py-2 mt-1.5"
                                    isLoading={isLoading}
                                    disabled={isLoading}
                                >
                                    Create Account
                                </Button>
                            </form>
                        )}

                        {/* Forgot Password Form */}
                        {mode === 'forgot-password' && (
                            <form onSubmit={handleForgotPassword} className="space-y-2.5">
                                <div>
                                    <label className="block text-xs font-medium text-foreground mb-1.5">
                                        Email Address
                                    </label>
                                    <Input
                                        type="email"
                                        placeholder="your@email.com"
                                        value={forgotPasswordEmail}
                                        onInput={(e) => setForgotPasswordEmail((e.target as HTMLInputElement).value)}
                                    />
                                    <p className="mt-1.5 text-xs text-muted-foreground">
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
                                <div className="relative my-2.5">
                                    <div className="absolute inset-0 flex items-center">
                                        <div className="w-full border-t border-border"></div>
                                    </div>
                                    <div className="relative flex justify-center text-xs">
                                        <span className="px-2 bg-background text-muted-foreground">Or continue with</span>
                                    </div>
                                </div>

                                <Button
                                    variant="outline"
                                    className="w-full text-xs py-2"
                                    onClick={handleGoogleLogin}
                                    disabled={isLoading}
                                >
                                    <Icon name="Chrome" className="w-3.5 h-3.5 mr-0.5" />
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
