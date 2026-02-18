// =============================================================================
// OAuth Callback Handler
// Handles the redirect after successful Google OAuth login
// =============================================================================

import { useEffect, useState } from "preact/hooks";
import { route } from "preact-router";
import { Icon } from "../../components/atoms/Icon/Icon";
import { BackgroundGradientAnimation } from "../../components/atoms/BackgroundGradientAnimation/BackgroundGradientAnimation";
import { APP_CONFIG } from "../../config";
import { authService } from "../../services/auth";

export function OAuthCallbackPage() {
  const [status, setStatus] = useState<"processing" | "success" | "error">(
    "processing",
  );
  const [message, setMessage] = useState("Processing authentication...");

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      // Get token and user type from URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get("token");
      const userType = urlParams.get("type") || "user";
      const newUser = urlParams.get("new_user") === "true";

      if (!token) {
        throw new Error("No authentication token received");
      }

      // Store token and user type
      localStorage.setItem(APP_CONFIG.TOKEN_STORAGE_KEY, token);
      localStorage.setItem(APP_CONFIG.USER_TYPE_STORAGE_KEY, userType);

      // Fetch and store user profile data
      setMessage("Fetching your profile...");
      const user = await authService.getCurrentUser();
      authService.setUser(user, userType as any);

      setStatus("success");
      setMessage("Login successful! Redirecting...");

      // Redirect based on profile completion status
      setTimeout(() => {
        if (newUser) {
          // New users need to complete their profile
          route(`/complete-profile?type=${userType}`);
        } else {
          // Existing users go to dashboard with full page refresh
          window.location.href = "/dashboard";
        }
      }, 1500);
    } catch (error) {
      console.error("OAuth callback error:", error);
      setStatus("error");
      setMessage(
        error instanceof Error ? error.message : "Authentication failed",
      );

      // Redirect to login page after a delay
      setTimeout(() => {
        route("/");
      }, 3000);
    }
  };

  return (
    <div className="relative h-screen overflow-hidden flex items-center justify-center">
      {/* Background Animation */}
      <div className="absolute inset-0">
        <BackgroundGradientAnimation />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center max-w-md mx-auto px-6">
        <div className="bg-card/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-border/50">
          {status === "processing" && (
            <>
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary mx-auto mb-6"></div>
              <h2 className="text-2xl font-bold text-foreground mb-3">
                Signing you in...
              </h2>
              <p className="text-muted-foreground">{message}</p>
            </>
          )}

          {status === "success" && (
            <>
              <div className="mx-auto mb-6 h-16 w-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <Icon
                  name="CheckCircle"
                  className="text-green-600 dark:text-green-400 h-10 w-10"
                />
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-3">
                Welcome!
              </h2>
              <p className="text-muted-foreground">{message}</p>
            </>
          )}

          {status === "error" && (
            <>
              <div className="mx-auto mb-6 h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <Icon
                  name="XCircle"
                  className="text-red-600 dark:text-red-400 h-10 w-10"
                />
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-3">
                Authentication Failed
              </h2>
              <p className="text-muted-foreground mb-4">{message}</p>
              <p className="text-sm text-muted-foreground">
                Redirecting to login page...
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
