// =============================================================================
// Veritas Protocol - Main App Component
// =============================================================================

import { useState } from 'preact/hooks';
import Router, { route } from 'preact-router';
import { Dashboard } from './pages/Dashboard/Dashboard';
import { NewIncidentPage } from './pages/NewIncident/NewIncident';
import { IncidentDetailPage } from './pages/IncidentDetail/IncidentDetail';
import { IncidentWorkspacePage } from './pages/IncidentWorkspace/IncidentWorkspace';
import { LawyerFinderPage } from './pages/LawyerFinder/LawyerFinder';
import { EvidenceVaultPage } from './pages/EvidenceVault/EvidenceVault';
import { LawbookPage } from './pages/Lawbook/Lawbook';
import { AuthPage } from './pages/Auth/Auth';
import { Settings } from './pages/Settings/Settings';
import { AIChatPage } from './pages/AIChat/AIChat';
import { ThemeProvider } from './hooks/useTheme';
import { AuthProvider, useAuth } from './hooks/useAuth';
import type { Incident, NavItem } from './types';
import type { WizardData } from './components/organisms/OnboardingWizard/OnboardingWizard';
import './index.css';

function AppContent() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
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
    return <AuthPage onSuccess={() => route('/dashboard')} />;
  }

  const handleNavigate = (item: NavItem) => {
    console.log('Navigate to:', item.href);
    route(item.href);
  };

  const handleNewIncident = () => {
    route('/new-incident');
  };

  const handleViewIncident = (incident: Incident) => {
    setSelectedIncident(incident);
    route('/incident-detail');
  };

  const handleWizardComplete = (data: WizardData) => {
    console.log('Wizard completed with data:', data);
    setWizardData(data);
    route('/incident-workspace');
  };

  const handleWizardCancel = () => {
    route('/dashboard');
  };

  const handleBackToDashboard = () => {
    setSelectedIncident(null);
    setWizardData(null);
    route('/dashboard');
  };

  const handleFindLawyers = () => {
    route('/lawyers');
  };

  return (
    <Router>
      <Dashboard
        path="/dashboard"
        default
        onNavigate={handleNavigate}
        onNewIncident={handleNewIncident}
        onViewIncident={handleViewIncident}
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
      <EvidenceVaultPage
        path="/evidence"
        onNavigate={handleNavigate}
      />
      <LawbookPage
        path="/lawbook"
        onNavigate={handleNavigate}
      />
      <AIChatPage
        path="/ai-chat"
        onNavigate={handleNavigate}
      />
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
