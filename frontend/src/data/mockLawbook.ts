import type { LawbookChapter } from '../types';

export const mockLawbookData: LawbookChapter[] = [
    {
        id: 'chap_cyberbullying',
        title: 'Cyberbullying & Harassment',
        icon: 'MessageSquareWarning',
        sections: [
            {
                id: 'sec_def',
                title: 'Definition & Overview',
                content: `
# Cyberbullying Defined

Cyberbullying involves the use of electronic communication to bully a person, typically by sending messages of an intimidating or threatening nature. 

**Key Characteristics:**
- **Intent:** The behavior is intentional, not accidental.
- **Repetition:** It reflects a pattern of behavior, not a single isolated incident.
- **Power Imbalance:** The perpetrator has perceived or actual power over the victim.

Under the *Information Technology Act, 2000*, various sections address different forms of cyber-crimes that encompass cyberbullying.
        `
            },
            {
                id: 'sec_laws',
                title: 'Relevant Laws (IT Act)',
                content: `
# Relevant Legal Sections

### Section 66E - Violation of Privacy
Punishment for violation of privacy. Whoever, intentionally or knowingly captures, publishes or transmits the image of a private area of any person without his or her consent, under circumstances violating the privacy of that person.

**Penalty:** Imprisonment up to three years or fine not exceeding two lakh rupees, or both.

### Section 67 - Obscene Material
Punishment for publishing or transmitting obscene material in electronic form.

### Section 507 IPC - Criminal Intimidation
Criminal intimidation by an anonymous communication.
        `
            },
            {
                id: 'sec_action',
                title: 'Taking Action',
                content: `
# Immediate Steps to Take

1. **Do not respond:** Engaging often escalates the situation.
2. **Collect Evidence:** Take screenshots, save messages, and record URLs. Use the *Evidence Vault* in this app to store them securely.
3. **Report:** Report the content to the platform (Instagram, Twitter, etc.).
4. **Legal Action:** If the threat is imminent or severe, contact local authorities immediately.
        `
            }
        ]
    },
    {
        id: 'chap_privacy',
        title: 'Data Privacy & Protection',
        icon: 'Shield',
        sections: [
            {
                id: 'sec_personal_data',
                title: 'Personal Data Rights',
                content: `
# Your Rights Over Personal Data

You have the right to:
- **Access:** Know what data is being collected about you.
- **Correction:** Request correction of inaccurate data.
- **Erasure:** Request deletion of data (Right to be Forgotten) under specific circumstances.

*Note: The Digital Personal Data Protection Act (DPDP) introduces significant rights for individuals.*
        `
            },
            {
                id: 'sec_breach',
                title: 'Handling Data Breaches',
                content: `
# What to do in a Data Breach

If you suspect your data has been leaked:
1. **Change Passwords:** Immediately update passwords for affected accounts.
2. **Enable 2FA:** Turn on Two-Factor Authentication.
3. **Monitor Accounts:** Watch financial statements for unauthorized activity.
        `
            }
        ]
    },
    {
        id: 'chap_stalking',
        title: 'Online Stalking',
        icon: 'Eye',
        sections: [
            {
                id: 'sec_stalking_rec',
                title: 'Recognizing Stalking',
                content: `
# recognizing Online Stalking (Cyberstalking)

Cyberstalking is the use of the Internet or other electronic means to stalk or harass an individual, group, or organization. It may include:
- False accusations
- Monitoring
- Making threats
- Identity theft
- Data destruction or manipulation
        `
            },
            {
                id: 'sec_stalking_law',
                title: 'Section 354D IPC',
                content: `
# Section 354D of Indian Penal Code

Defines stalking as:
1. Following a woman and contacting or attempting to contact such woman to foster personal interaction repeatedly despite a clear indication of disinterest.
2. Monitoring the use by a woman of the internet, email, or any other form of electronic communication.

**Penalty:**
- First conviction: Imprisonment up to 3 years + fine.
- Second conviction: Imprisonment up to 5 years + fine.
        `
            }
        ]
    }
];
