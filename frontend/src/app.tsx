// =============================================================================
// Veritas Protocol - Main App Component
// =============================================================================

import { useState } from 'preact/hooks';
import { Dashboard } from './pages/Dashboard/Dashboard';
import { NewIncidentPage } from './pages/NewIncident/NewIncident';
import { IncidentDetailPage } from './pages/IncidentDetail/IncidentDetail';
import { IncidentWorkspacePage } from './pages/IncidentWorkspace/IncidentWorkspace';
import { LawyerFinderPage } from './pages/LawyerFinder/LawyerFinder';
import { EvidenceVaultPage } from './pages/EvidenceVault/EvidenceVault';
import { LawbookPage } from './pages/Lawbook/Lawbook';
import { mockUser } from './data/mockData';
import { ThemeProvider } from './hooks/useTheme';
import type { Incident, NavItem } from './types';
import type { WizardData } from './components/organisms/OnboardingWizard/OnboardingWizard';
import './index.css';

type Page = 'dashboard' | 'new-incident' | 'incident-detail' | 'incident-workspace' | 'lawyer-finder' | 'evidence-vault' | 'lawbook';

function AppContent() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [wizardData, setWizardData] = useState<WizardData | null>(null);

  const handleNavigate = (item: NavItem) => {
    console.log('Navigate to:', item.href);
    // Map navigation items to pages
    if (item.href === '/') {
      setCurrentPage('dashboard');
    } else if (item.href === '/lawyers') {
      setCurrentPage('lawyer-finder');
    } else if (item.href === '/evidence') {
      setCurrentPage('evidence-vault');
    } else if (item.href === '/lawbook') {
      setCurrentPage('lawbook');
    }
  };

  const handleNewIncident = () => {
    setCurrentPage('new-incident');
  };

  const handleViewIncident = (incident: Incident) => {
    setSelectedIncident(incident);
    setCurrentPage('incident-detail');
  };

  const handleWizardComplete = (data: WizardData) => {
    console.log('Wizard completed with data:', data);
    // Store wizard data and navigate to workspace
    setWizardData(data);
    setCurrentPage('incident-workspace');
  };

  const handleWizardCancel = () => {
    setCurrentPage('dashboard');
  };

  const handleBackToDashboard = () => {
    setSelectedIncident(null);
    setWizardData(null);
    setCurrentPage('dashboard');
  };

  const handleFindLawyers = () => {
    setCurrentPage('lawyer-finder');
  };

  // Render current page
  switch (currentPage) {
    case 'new-incident':
      return (
        <NewIncidentPage
          user={mockUser}
          onNavigate={handleNavigate}
          onComplete={handleWizardComplete}
          onCancel={handleWizardCancel}
        />
      );

    case 'incident-workspace':
      return (
        <IncidentWorkspacePage
          user={mockUser}
          wizardData={wizardData || undefined}
          onNavigate={handleNavigate}
          onBack={handleBackToDashboard}
          onFindLawyers={handleFindLawyers}
        />
      );

    case 'incident-detail':
      if (!selectedIncident) {
        setCurrentPage('dashboard');
        return null;
      }
      return (
        <IncidentDetailPage
          user={mockUser}
          incident={selectedIncident}
          onNavigate={handleNavigate}
          onBack={handleBackToDashboard}
        />
      );

    case 'lawyer-finder':
      return (
        <LawyerFinderPage
          user={mockUser}
          onNavigate={handleNavigate}
          onBack={handleBackToDashboard}
        />
      );

    case 'evidence-vault':
      return (
        <EvidenceVaultPage
          onNavigate={handleNavigate}
        />
      );

    case 'lawbook':
      return (
        <LawbookPage
          onNavigate={handleNavigate}
        />
      );

    default:
      return (
        <Dashboard
          onNavigate={handleNavigate}
          onNewIncident={handleNewIncident}
          onViewIncident={handleViewIncident}
        />
      );
  }
}

export function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
