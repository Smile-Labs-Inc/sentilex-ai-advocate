// =============================================================================
// Veritas Protocol - Main App Component
// =============================================================================

import { useState } from "preact/hooks";
import Router, { route } from "preact-router";
import { Dashboard } from "./pages/Dashboard/Dashboard";
import { IncidentsPage } from "./pages/Incidents/Incidents";
import { NewIncidentPage } from "./pages/NewIncident/NewIncident";
import { IncidentDetailPage } from "./pages/IncidentDetail/IncidentDetail";
import { IncidentWorkspacePage } from "./pages/IncidentWorkspace/IncidentWorkspace";
import { LawyerFinderPage } from "./pages/LawyerFinder/LawyerFinder";
import { EvidenceVaultPage } from "./pages/EvidenceVault/EvidenceVault";
import { EvidencePreview } from "./pages/EvidencePreview/EvidencePreview";
import { LawbookPage } from "./pages/Lawbook/Lawbook";
import { AuthPage } from "./pages/Auth/Auth";
import { Settings } from "./pages/Settings/Settings";
import { AIChatPage } from "./pages/AIChat/AIChat";
import { VerifyEmailPage } from "./pages/VerifyEmail/VerifyEmail";
import { ThemeProvider } from "./hooks/useTheme";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import type { Incident, NavItem } from "./types";
import type { WizardData } from "./components/organisms/OnboardingWizard/OnboardingWizard";
import "./index.css";

function AppContent() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(
    null,
  );
  const [wizardData, setWizardData] = useState<WizardData | null>(null);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show auth page if not authenticated or no user data
  if (!isAuthenticated || !user) {
    return <AuthPage onSuccess={() => route("/dashboard")} />;
  }

  const handleNavigate = (item: NavItem) => {
    console.log("Navigate to:", item.href);
    route(item.href);
  };

  const handleNewIncident = () => {
    route("/new-incident");
  };

  const handleViewAllIncidents = () => {
    route("/dashboard");
  };

  const handleViewIncident = (incident: Incident) => {
    setSelectedIncident(incident);
    route("/incident-workspace");
  };

  const handleWizardComplete = (data: WizardData) => {
    console.log("Wizard completed with data:", data);
    setWizardData(data);
    route("/incident-workspace");
  };

  const handleWizardCancel = () => {
    route("/dashboard");
  };

  const handleBackToDashboard = () => {
    setSelectedIncident(null);
    setWizardData(null);
    route("/dashboard");
  };

  const handleFindLawyers = () => {
    route("/lawyers");
  };

  const handleIncidentsUpdated = () => {
    // Force re-render by navigating to the current route
    window.location.reload();
  };

  return (
    <Router>
      <Dashboard
        path="/dashboard"
        default
        onNavigate={handleNavigate}
        onNewIncident={handleNewIncident}
        onViewIncident={handleViewIncident}
        onIncidentsUpdated={handleIncidentsUpdated}
      />
      <IncidentsPage
        path="/incidents"
        onNavigate={handleNavigate}
        onNewIncident={handleNewIncident}
        onViewIncident={handleViewIncident}
        onIncidentsUpdated={handleIncidentsUpdated}
      />
      <NewIncidentPage
        path="/new-incident"
        user={user}
        onNavigate={handleNavigate}
        onComplete={handleWizardComplete}
        onCancel={handleWizardCancel}
      />
      <IncidentWorkspacePage
        path="/incident-workspace"
        user={user}
        wizardData={wizardData || undefined}
        incident={selectedIncident || undefined}
        onNavigate={handleNavigate}
        onBack={handleBackToDashboard}
        onFindLawyers={handleFindLawyers}
      />
      <IncidentDetailPage
        path="/incident-detail"
        user={user}
        incident={selectedIncident || undefined}
        onNavigate={handleNavigate}
        onBack={handleBackToDashboard}
      />
      <LawyerFinderPage
        path="/lawyers"
        user={user}
        onNavigate={handleNavigate}
        onBack={handleBackToDashboard}
      />
      <EvidenceVaultPage path="/evidence" onNavigate={handleNavigate} />
      <EvidencePreview path="/evidence-preview/:id" />
      <LawbookPage path="/lawbook" onNavigate={handleNavigate} />
      <AIChatPage path="/ai-chat" onNavigate={handleNavigate} />
      <VerifyEmailPage path="/verify-email" />
      <Settings path="/settings" />
    </Router>
  );
}

export function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
