// =============================================================================
// Reset Password Page
// Allows users to set a new password using the token from their email
// =============================================================================

import { useState, useEffect } from "preact/hooks";
import { route } from "preact-router";
import { Button } from "../../components/atoms/Button/Button";
import { Input } from "../../components/atoms/Input/Input";
import { authService } from "../../services/auth";
import type { PasswordResetConfirm } from "../../types/auth";

interface ResetPasswordPageProps {
  path: string;
}

export function ResetPasswordPage({ path }: ResetPasswordPageProps) {
  const [token, setToken] = useState<string>("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<"form" | "success" | "error">("form");
  const [message, setMessage] = useState("");

  // Password validation state
  const [passwordValidation, setPasswordValidation] = useState({
    minLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasDigit: false,
    hasSpecial: false,
    passwordsMatch: true,
  });

  useEffect(() => {
    // Get token from URL
    const urlParams = new URLSearchParams(window.location.search);
    const tokenParam = urlParams.get("token");

    if (!tokenParam) {
      setStatus("error");
      setMessage("No reset token provided. Please use the link from your email.");
      return;
    }

    setToken(tokenParam);
  }, []);

  // Validate password in real-time
  const validatePassword = (pwd: string, confirmPwd: string) => {
    setPasswordValidation({
      minLength: pwd.length >= 8,
      hasUppercase: /[A-Z]/.test(pwd),
      hasLowercase: /[a-z]/.test(pwd),
      hasDigit: /\d/.test(pwd),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
      passwordsMatch: !confirmPwd || pwd === confirmPwd,
    });
  };

  const handlePasswordChange = (e: Event) => {
    const value = (e.target as HTMLInputElement).value;
    setPassword(value);
    validatePassword(value, confirmPassword);
  };

  const handleConfirmPasswordChange = (e: Event) => {
    const value = (e.target as HTMLInputElement).value;
    setConfirmPassword(value);
    validatePassword(password, value);
  };

  const isPasswordValid = () => {
    return (
      passwordValidation.minLength &&
      passwordValidation.hasUppercase &&
      passwordValidation.hasLowercase &&
      passwordValidation.hasDigit &&
      passwordValidation.hasSpecial &&
      passwordValidation.passwordsMatch
    );
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();

    if (!token) {
      setStatus("error");
      setMessage("Invalid reset token.");
      return;
    }

    if (!isPasswordValid()) {
      setMessage("Please ensure your password meets all requirements.");
      return;
    }

    setIsLoading(true);
    setMessage("");

    try {
      const data: PasswordResetConfirm = {
        token,
        new_password: password,
      };

      const response = await authService.confirmPasswordReset(data);
      setStatus("success");
      setMessage(response.message || "Password reset successfully!");

      // Redirect to login after 3 seconds
      setTimeout(() => {
        route("/dashboard");
      }, 3000);
    } catch (error: any) {
      setStatus("error");
      setMessage(
        error.message ||
        "Failed to reset password. The link may be expired or invalid.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-card rounded-lg shadow-lg p-8">
        {status === "form" && (
          <>
            <h2 className="text-2xl font-semibold text-foreground mb-2 text-center">
              Reset Your Password
            </h2>
            <p className="text-muted-foreground text-center mb-6">
              Enter your new password below
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  New Password
                </label>
                <Input
                  type="password"
                  placeholder="Enter new password"
                  value={password}
                  onInput={handlePasswordChange}
                  disabled={isLoading || !token}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Confirm Password
                </label>
                <Input
                  type="password"
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onInput={handleConfirmPasswordChange}
                  disabled={isLoading || !token}
                />
              </div>

              {/* Password Requirements */}
              <div className="space-y-1.5 text-xs">
                <p className="font-medium text-foreground">
                  Password must contain:
                </p>
                <div className="space-y-1">
                  <p
                    className={
                      passwordValidation.minLength
                        ? "text-green-600"
                        : "text-muted-foreground"
                    }
                  >
                    {passwordValidation.minLength ? "✓" : "○"} At least 8
                    characters
                  </p>
                  <p
                    className={
                      passwordValidation.hasUppercase
                        ? "text-green-600"
                        : "text-muted-foreground"
                    }
                  >
                    {passwordValidation.hasUppercase ? "✓" : "○"} One uppercase
                    letter
                  </p>
                  <p
                    className={
                      passwordValidation.hasLowercase
                        ? "text-green-600"
                        : "text-muted-foreground"
                    }
                  >
                    {passwordValidation.hasLowercase ? "✓" : "○"} One lowercase
                    letter
                  </p>
                  <p
                    className={
                      passwordValidation.hasDigit
                        ? "text-green-600"
                        : "text-muted-foreground"
                    }
                  >
                    {passwordValidation.hasDigit ? "✓" : "○"} One number
                  </p>
                  <p
                    className={
                      passwordValidation.hasSpecial
                        ? "text-green-600"
                        : "text-muted-foreground"
                    }
                  >
                    {passwordValidation.hasSpecial ? "✓" : "○"} One special
                    character
                  </p>
                  <p
                    className={
                      passwordValidation.passwordsMatch
                        ? "text-green-600"
                        : "text-red-600"
                    }
                  >
                    {passwordValidation.passwordsMatch ? "✓" : "✗"} Passwords
                    match
                  </p>
                </div>
              </div>

              {message && status === "error" && (
                <div className="text-red-600 text-sm text-center">
                  {message}
                </div>
              )}

              <Button
                variant="primary"
                className="w-full"
                isLoading={isLoading}
                disabled={isLoading || !token || !isPasswordValid()}
              >
                Reset Password
              </Button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => route("/dashboard")}
                  className="text-sm text-primary hover:underline"
                  disabled={isLoading}
                >
                  Back to Login
                </button>
              </div>
            </form>
          </>
        )}

        {status === "success" && (
          <>
            <div className="text-green-500 mb-4">
              <svg
                className="w-16 h-16 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-foreground mb-2 text-center">
              Password Reset Successful!
            </h2>
            <p className="text-muted-foreground text-center mb-4">{message}</p>
            <p className="text-sm text-muted-foreground text-center">
              Redirecting to login...
            </p>
          </>
        )}

        {status === "error" && !token && (
          <>
            <div className="text-red-500 mb-4">
              <svg
                className="w-16 h-16 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-foreground mb-2 text-center">
              Invalid Reset Link
            </h2>
            <p className="text-muted-foreground text-center mb-6">{message}</p>
            <button
              onClick={() => route("/dashboard")}
              className="w-full px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              Go to Login
            </button>
          </>
        )}
      </div>
    </div>
  );
}
