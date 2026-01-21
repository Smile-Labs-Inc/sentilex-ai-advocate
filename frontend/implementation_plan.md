# Implementation Plan: Evidence Vault & Lawbook

## Overview
This plan outlines the steps to implement the **Evidence Vault** and **Lawbook** (formerly Help Center) features for the Veritas Protocol frontend. The implementation follows the Atomic Design methodology (Atoms, Molecules, Organisms, Templates, Pages) to maintain code organization and scalability.

## 1. Navigation & Routing Updates

### 1.1 Update Navigation Data
**File:** `src/data/navigation.ts`
- **Change:** Rename "Help Center" to "Lawbook".
- **Update:** Ensure `href` for Lawbook is `/lawbook`.
- **Verify:** "Evidence Vault" exists with `href: '/evidence-vault'` (or update existing entry).

### 1.2 Update Type Definitions
**File:** `src/types/index.ts`
- **Update:** Extend the `Page` type union to include `'evidence-vault'` and `'lawbook'`.
- **Add:** New types for `LawbookChapter`, `LawbookSection`, and `Bookmark`.

### 1.3 App Routing
**File:** `src/App.tsx`
- **Update:** Add logic in `AppContent` to handle routing for `evidence-vault` and `lawbook`.
- **Import:** Import the new page components (to be created).

## 2. Data Layer (Mock Data)

### 2.1 Evidence Vault Data
**File:** `src/data/mockEvidenceVault.ts` (New)
- **Create:** `mockEvidenceVaultItems` array using the existing `Evidence` type.
- **Content:** diverse set of evidence types (image, video, document) with various dates and descriptions to test sorting/filtering.

### 2.2 Lawbook Data
**File:** `src/data/mockLawbook.ts` (New)
- **Create:** `mockLawbookContent` structure.
- **Structure:**
  ```typescript
  export interface LawbookChapter {
    id: string;
    title: string;
    sections: {
      id: string;
      title: string;
      content: string; // Markdown content
    }[];
  }
  ```
- **Content:** Dummy legal text (Markdown format) covering relevant topics (e.g., Cyberbullying, Data Privacy).

## 3. Component Architecture (Atomic Design)

### 3.1 Atoms (Reusing Existing)
- `Button`: For actions (Delete, Sort, Bookmark).
- `Badge`: For identifying evidence types or tags.
- `Input`: For search bars.
- `Icon`: For visual indicators.

### 3.2 Molecules
- **EvidenceVaultCard** (`src/components/molecules/EvidenceVaultCard/EvidenceVaultCard.tsx`)
  - **Purpose:** Display single evidence item details.
  - **Props:** `evidence: Evidence`, `onDelete: (id) => void`.
  - **Layout:** Thumbnail (icon or image), Title, Type Badge, Date, Delete Button.
  
- **LawbookSidebarItem** (`src/components/molecules/LawbookSidebarItem/LawbookSidebarItem.tsx`)
  - **Purpose:** Navigation item for Lawbook chapters.
  - **Props:** `chapter: LawbookChapter`, `isActive: boolean`, `onClick: () => void`.

- **ChatMessage** (`src/components/molecules/ChatMessage/ChatMessage.tsx`)
  - **Refactor:** Considerations to extract this from `AIChatSection` if beneficial, or create a similar one for Lawbook.

### 3.3 Organisms
- **EvidenceVaultGrid** (`src/components/organisms/EvidenceVaultGrid/EvidenceVaultGrid.tsx`)
  - **Purpose:** Grid layout of `EvidenceVaultCard`s with toolbar.
  - **Features:** 
    - Toolbar: Search input, Sort dropdown (Date, Type, Name), Filter toggles.
    - Grid: Responsive grid of cards.
  
- **LawbookViewer** (`src/components/organisms/LawbookViewer/LawbookViewer.tsx`)
  - **Purpose:** Main reading interface.
  - **Features:**
    - Sidebar: List of chapters.
    - Content Area: Render Markdown content.
    - Bookmark Toggle: Floating or header button to bookmark current section.

- **LawbookChat** (`src/components/organisms/LawbookChat/LawbookChat.tsx`)
  - **Purpose:** Context-aware AI chat for the Lawbook.
  - **Base:** Similar to `AIChatSection` but styled to sit alongside the law text (e.g., sticky sidebar or overlay).

### 3.4 Templates
- **EvidenceVaultTemplate** (`src/components/templates/EvidenceVaultTemplate/EvidenceVaultTemplate.tsx`)
  - **Layout:** Header (Title + Global Stats maybe?), Main Content (Vault Grid).

- **LawbookTemplate** (`src/components/templates/LawbookTemplate/LawbookTemplate.tsx`)
  - **Layout:** Sidebar (Chapters), Main Content (Viewer), Right Panel (AI Chat).

### 3.5 Pages
- **EvidenceVaultPage** (`src/pages/EvidenceVault/EvidenceVault.tsx`)
  - **Logic:**
    - State: `items` (from mock data), `filter`, `sortOrder`.
    - Handlers: `handleDelete`, `handleSort`, `handleFilter`.
  
- **LawbookPage** (`src/pages/Lawbook/Lawbook.tsx`)
  - **Logic:**
    - State: `activeChapter`, `bookmarks` (Set<string>), `chatMessages`.
    - Handlers:Navigating chapters, toggling bookmarks, sending chat messages.

## 4. Workflows

### 4.1 "Evidence Vault" Flow
1. User clicks "Evidence Vault" in Sidebar.
2. `App.tsx` renders `EvidenceVaultPage`.
3. Page loads `mockEvidenceVaultItems`.
4. User can:
   - **Sort:** By Date (Newest/Oldest), Type.
   - **Delete:** Click trash icon -> Modal/Confirm -> Remove from state.

### 4.2 "Lawbook" Flow
1. User clicks "Lawbook" in Sidebar.
2. `App.tsx` renders `LawbookPage`.
3. Default chapter is shown.
4. User can:
   - **Navigate:** Click chapters in sidebar.
   - **Bookmark:** Click bookmark icon on a section.
   - **Chat:** Type "What does Section 66A mean?" in the side chat to get "response" (dummy response or logic).

## 5. Next Steps

1. **Approval:** Wait for user approval of this plan.
2. **Scaffold:** Create directories and files for new components.
3. **Data:** Populate mock data files.
4. **Implement:** Build components from Atoms up to Pages.
5. **Integrate:** Wire up routing in `App.tsx`.
