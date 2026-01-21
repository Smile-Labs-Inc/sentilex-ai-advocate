// =============================================================================
// Wizard Questions Configuration
// Central configuration for incident reporting wizard
// =============================================================================

import type { WizardQuestion, IncidentType } from '../types';

// =============================================================================
// Question Definitions
// =============================================================================

export const wizardQuestions: WizardQuestion[] = [
    // Step 1: Incident Type (existing, enhanced)
    {
        id: 'incident-type',
        question: 'What type of incident are you reporting?',
        description: 'Select the category that best describes what happened.',
        type: 'radio',
        required: true,
        options: [
            {
                value: 'cyberbullying',
                label: 'Cyberbullying',
                description: 'Repeated harassment, threats, or intimidation online',
                icon: 'MessageSquareWarning',
            },
            {
                value: 'harassment',
                label: 'Harassment',
                description: 'Unwanted contact, threats, or offensive behavior',
                icon: 'AlertTriangle',
            },
            {
                value: 'stalking',
                label: 'Stalking',
                description: 'Persistent tracking, monitoring, or following',
                icon: 'Eye',
            },
            {
                value: 'non-consensual-leak',
                label: 'Non-consensual Intimate Images',
                description: 'Sharing private images without consent',
                icon: 'ImageOff',
            },
            {
                value: 'identity-theft',
                label: 'Identity Theft',
                description: 'Impersonation or misuse of personal information',
                icon: 'UserX',
            },
            {
                value: 'online-fraud',
                label: 'Online Fraud',
                description: 'Scams, phishing, or financial fraud',
                icon: 'CreditCard',
            },
            {
                value: 'other',
                label: 'Other',
                description: 'Another type of cybercrime not listed above',
                icon: 'FileQuestion',
            },
        ],
    },

    // Step 2: Sub-category - Cyberbullying
    {
        id: 'cyberbullying-type',
        question: 'What form did the cyberbullying take?',
        description: 'Select all that apply.',
        type: 'checkbox',
        required: true,
        dependsOn: { questionId: 'incident-type', values: ['cyberbullying'] },
        options: [
            { value: 'verbal-abuse', label: 'Verbal abuse or insults', icon: 'MessageCircle' },
            { value: 'threats', label: 'Threats of harm', icon: 'AlertOctagon' },
            { value: 'doxxing', label: 'Sharing personal information (doxxing)', icon: 'MapPin' },
            { value: 'impersonation', label: 'Impersonation or fake accounts', icon: 'UserX' },
            { value: 'exclusion', label: 'Deliberate exclusion from groups', icon: 'UserMinus' },
            { value: 'rumor-spreading', label: 'Spreading rumors or false information', icon: 'Share2' },
        ],
    },

    // Step 2: Sub-category - Harassment
    {
        id: 'harassment-type',
        question: 'What type of harassment occurred?',
        description: 'Select all that apply.',
        type: 'checkbox',
        required: true,
        dependsOn: { questionId: 'incident-type', values: ['harassment'] },
        options: [
            { value: 'unwanted-contact', label: 'Unwanted messages or calls', icon: 'PhoneOff' },
            { value: 'sexual', label: 'Sexual harassment', icon: 'AlertTriangle' },
            { value: 'workplace', label: 'Workplace harassment', icon: 'Briefcase' },
            { value: 'discriminatory', label: 'Discriminatory harassment', icon: 'Ban' },
            { value: 'intimidation', label: 'Intimidation or coercion', icon: 'Shield' },
        ],
    },

    // Step 2: Sub-category - Stalking
    {
        id: 'stalking-type',
        question: 'How are you being stalked?',
        description: 'Select all that apply.',
        type: 'checkbox',
        required: true,
        dependsOn: { questionId: 'incident-type', values: ['stalking'] },
        options: [
            { value: 'location-tracking', label: 'Location tracking', icon: 'MapPin' },
            { value: 'social-media', label: 'Social media monitoring', icon: 'Eye' },
            { value: 'physical-following', label: 'Physical following', icon: 'Footprints' },
            { value: 'unwanted-gifts', label: 'Unwanted gifts or contact', icon: 'Gift' },
            { value: 'device-spyware', label: 'Spyware or device monitoring', icon: 'Smartphone' },
        ],
    },

    // Step 3: When did it occur
    {
        id: 'incident-date',
        question: 'When did this incident first occur?',
        description: 'Provide the date when you first noticed this behavior.',
        type: 'date',
        required: true,
    },

    // Step 4: Is it ongoing?
    {
        id: 'is-ongoing',
        question: 'Is this incident still ongoing?',
        type: 'radio',
        required: true,
        options: [
            { value: 'yes', label: 'Yes, it is still happening', icon: 'Clock' },
            { value: 'no', label: 'No, it has stopped', icon: 'CheckCircle' },
            { value: 'unsure', label: "I'm not sure", icon: 'HelpCircle' },
        ],
    },

    // Step 5: Platforms involved
    {
        id: 'platforms',
        question: 'Where did this happen?',
        description: 'Select all platforms or locations involved.',
        type: 'checkbox',
        required: true,
        options: [
            { value: 'instagram', label: 'Instagram', icon: 'Instagram' },
            { value: 'facebook', label: 'Facebook', icon: 'Facebook' },
            { value: 'twitter', label: 'Twitter/X', icon: 'Twitter' },
            { value: 'whatsapp', label: 'WhatsApp', icon: 'MessageCircle' },
            { value: 'snapchat', label: 'Snapchat', icon: 'Camera' },
            { value: 'tiktok', label: 'TikTok', icon: 'Video' },
            { value: 'email', label: 'Email', icon: 'Mail' },
            { value: 'sms', label: 'SMS/Text Messages', icon: 'Smartphone' },
            { value: 'gaming', label: 'Gaming Platforms', icon: 'Gamepad2' },
            { value: 'other', label: 'Other', icon: 'Globe' },
        ],
    },

    // Step 6: Perpetrator known
    {
        id: 'perpetrator-known',
        question: 'Do you know who is responsible?',
        type: 'radio',
        required: true,
        options: [
            { value: 'yes-identity', label: 'Yes, I know their real identity', icon: 'User' },
            { value: 'yes-username', label: 'Yes, but only their username/handle', icon: 'AtSign' },
            { value: 'no', label: "No, I don't know who they are", icon: 'UserX' },
        ],
    },

    // Step 6b: Perpetrator details
    {
        id: 'perpetrator-details',
        question: 'What information do you have about the perpetrator?',
        description: 'Provide any identifying information you have.',
        type: 'textarea',
        required: false,
        placeholder: 'Username, real name, profile links, or any other identifying details...',
        dependsOn: { questionId: 'perpetrator-known', values: ['yes-identity', 'yes-username'] },
    },

    // Step 7: Evidence collected
    {
        id: 'has-evidence',
        question: 'Have you collected any evidence?',
        description: 'Screenshots, messages, recordings, etc.',
        type: 'radio',
        required: true,
        options: [
            { value: 'yes', label: 'Yes, I have evidence saved', icon: 'FileCheck' },
            { value: 'some', label: 'I have some, but not everything', icon: 'FileMinus' },
            { value: 'no', label: 'No, I haven\'t collected any yet', icon: 'FileX' },
        ],
    },

    // Step 8: Previous reports
    {
        id: 'previous-reports',
        question: 'Have you reported this elsewhere?',
        type: 'checkbox',
        required: false,
        options: [
            { value: 'platform', label: 'Reported to the platform', icon: 'Flag' },
            { value: 'police', label: 'Filed a police report', icon: 'Shield' },
            { value: 'employer', label: 'Reported to employer/school', icon: 'Building' },
            { value: 'lawyer', label: 'Consulted a lawyer', icon: 'Scale' },
            { value: 'none', label: 'Not reported anywhere', icon: 'X' },
        ],
    },

    // Step 9: Incident title
    {
        id: 'incident-title',
        question: 'Give your case a title',
        description: 'A brief title to identify this incident.',
        type: 'text',
        required: true,
        placeholder: 'e.g., "Instagram harassment case"',
    },

    // Step 10: Description
    {
        id: 'incident-description',
        question: 'Describe what happened',
        description: 'Provide as much detail as possible. Include dates, times, and context.',
        type: 'textarea',
        required: true,
        placeholder: 'Start from the beginning and describe what happened...',
    },
];

// =============================================================================
// Helper Functions
// =============================================================================

export function getQuestionsForIncidentType(incidentType: IncidentType | ''): WizardQuestion[] {
    return wizardQuestions.filter(q => {
        // Always include questions without dependencies
        if (!q.dependsOn) return true;

        // Include if dependency matches
        return q.dependsOn.values.includes(incidentType);
    });
}

export function getQuestionById(id: string): WizardQuestion | undefined {
    return wizardQuestions.find(q => q.id === id);
}

export function validateAnswer(question: WizardQuestion, answer: string | string[]): boolean {
    if (!question.required) return true;

    if (Array.isArray(answer)) {
        return answer.length > 0;
    }

    return answer.trim() !== '';
}
