# Veritas Protocol

Veritas Protocol is a premium frontend application for an AI law consultancy firm, designed with a focus on high-fidelity aesthetics and modular architecture using the **Atomic Design** methodology.

## 🚀 Tech Stack

- **Framework**: [Preact](https://preactjs.com/) (Fast 3kB alternative to React)
- **Tooling**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4-alpha) (using the new `@tailwindcss/vite` engine)
- **Animations**: [Motion](https://motion.dev/)
- **Icons**: [Lucide Preact](https://lucide.dev/)
- **Charts**: [Visx](https://airbnb.io/visx/) (Powerful visualization primitives by Airbnb)

## 🏗 Architecture: Atomic Design

To maintain a scalable and manageable codebase for both humans and LLMs, we follow the Atomic Design methodology:

- **Atoms**: Basic building blocks (Buttons, Inputs, Badges, Typography).
- **Molecules**: Groups of atoms functioning together (Search Bars, Card Headers).
- **Organisms**: Complex UI components composed of molecules and atoms (Sidebars, Data Tables, Charts).
- **Templates**: Page-level layouts that define where components are placed.
- **Pages**: Specific instances where templates are populated with real or mock data.

## 🛠 Getting Started

### Prerequisites

- Node.js (v20 or higher recommended)
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/LazySeaHorse/veritas-protocol.git

# Install dependencies
npm install
```

### Development

```bash
# Start the development server
npm run dev
```

### Build

```bash
# Build for production
npm run build
```

## 🌐 Deployment

This project is configured for auto-deployment to **GitHub Pages** via GitHub Actions.

- **Workflow**: Any push to the `main` branch triggers a build.
- **SPA Support**: The build process automatically generates a `404.html` to handle client-side routing.
- **Base Path**: Configured in `vite.config.ts` to support subdirectory hosting.

## ⚖️ Legal AI Consulting

Veritas Protocol provides advanced legal analytics, automated incident reporting, and lawyer discovery tools powered by artificial intelligence.
