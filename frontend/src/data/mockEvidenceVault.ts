import type { Evidence } from '../types';

export const mockEvidenceVaultItems: Evidence[] = [
    {
        id: 'ev_001',
        fileName: 'threat_dm_screenshot.jpg',
        fileSize: 2450000,
        fileType: 'screenshot',
        mimeType: 'image/jpeg',
        uploadedAt: new Date('2026-01-15T14:30:00'),
        description: 'Screenshot of threatening direct messages on Instagram',
        isEncrypted: true,
        thumbnailUrl: 'https://placehold.co/400x300/18181b/fafafa?text=Screenshot'
    },
    {
        id: 'ev_002',
        fileName: 'voice_recording_call.mp3',
        fileSize: 5200000,
        fileType: 'audio',
        mimeType: 'audio/mpeg',
        uploadedAt: new Date('2026-01-12T09:15:00'),
        description: 'Recording of phone call received from unknown number',
        isEncrypted: true
    },
    {
        id: 'ev_003',
        fileName: 'harassment_log.pdf',
        fileSize: 1024000,
        fileType: 'document',
        mimeType: 'application/pdf',
        uploadedAt: new Date('2025-12-28T11:20:00'),
        description: 'Detailed log of all harassment incidents over December',
        isEncrypted: true
    },
    {
        id: 'ev_004',
        fileName: 'stalker_photo.jpg',
        fileSize: 3100000,
        fileType: 'image',
        mimeType: 'image/jpeg',
        uploadedAt: new Date('2026-01-17T08:00:00'),
        description: 'Photo of suspicious individual outside workplace',
        isEncrypted: true,
        thumbnailUrl: 'https://placehold.co/400x300/18181b/fafafa?text=Photo'
    },
    {
        id: 'ev_005',
        fileName: 'abusive_emails_export.zip',
        fileSize: 15400000,
        fileType: 'document',
        mimeType: 'application/zip',
        uploadedAt: new Date('2026-01-05T16:45:00'),
        description: 'Archive of abusive emails received',
        isEncrypted: true
    },
    {
        id: 'ev_006',
        fileName: 'cctv_footage.mp4',
        fileSize: 156000000,
        fileType: 'video',
        mimeType: 'video/mp4',
        uploadedAt: new Date('2026-01-16T10:00:00'),
        description: 'CCTV footage of vandalism incident',
        isEncrypted: true,
        thumbnailUrl: 'https://placehold.co/400x300/18181b/fafafa?text=Video'
    }
];
