// =============================================================================
// NewIncident Page
// Wizard for creating a new incident report
// =============================================================================

import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { OnboardingWizard, type WizardData } from '../../components/organisms/OnboardingWizard/OnboardingWizard';
import type { User, NavItem } from '../../types';

export interface NewIncidentPageProps {
    user: User;
    onNavigate: (item: NavItem) => void;
    onComplete: (data: WizardData) => void;
    onCancel: () => void;
}

export function NewIncidentPage({
    user,
    onNavigate,
    onComplete,
    onCancel,
}: NewIncidentPageProps) {
    return (
        <DashboardLayout
            user={user}
            currentPath="/new-incident"
            onNavigate={onNavigate}
        >
            <div className="max-w-4xl mx-auto py-8">
                <OnboardingWizard
                    onComplete={onComplete}
                    onCancel={onCancel}
                />
            </div>
        </DashboardLayout>
    );
}

export default NewIncidentPage;
