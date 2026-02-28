# StructIQ - AI-Powered Construction Intelligence Platform

## Overview

StructIQ is an enterprise-grade AI platform designed for civil engineers, contractors, and project managers. It automates construction workflows from drawing analysis to cost estimation and scheduling.

## Features

- **Automated QTO**: AI-powered quantity take-off from 2D drawings
- **Cost Intelligence**: Smart cost estimation with uncertainty bands
- **Smart Scheduling**: Phase-wise schedules with productivity logic
- **Validation Engine**: Confidence scoring and precision checks
- **Optimization**: AI-powered cost optimization suggestions
- **Supplier Management**: Verified supplier network and comparison
- **Procurement**: RFQ generation and supplier communication
- **Reports**: Export compliance-ready documentation

## Tech Stack

- **Frontend**: React 19
- **Styling**: Tailwind CSS
- **Architecture**: Functional components with hooks
- **Design System**: Custom warm color palette for construction industry

## Color System

The platform uses a warm, industrial color palette:

- **Brand Charcoal**: #1C1917 (Sidebar, headers)
- **Construction Orange**: #EA580C (Primary CTAs)
- **Warm Amber Gold**: #D97706 (Secondary actions)
- **Warm White**: #FAFAF9 (Page background)
- **Pure White**: #FFFFFF (Cards)

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button.js
│   ├── Card.js
│   ├── Badge.js
│   ├── Table.js
│   ├── ProgressBar.js
│   ├── Stepper.js
│   └── UploadZone.js
├── layouts/            # Layout components
│   ├── MainLayout.js
│   ├── Sidebar.js
│   └── Topbar.js
├── pages/              # Page components
│   ├── Landing.js
│   ├── Login.js
│   ├── Overview.js
│   ├── Upload.js
│   ├── QTO.js
│   ├── Cost.js
│   ├── Schedule.js
│   ├── Validation.js
│   ├── Optimization.js
│   ├── Suppliers.js
│   ├── Procurement.js
│   ├── Reports.js
│   └── Settings.js
├── App.js              # Main application component
└── index.js            # Entry point
```

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm start
```

The application will open at [http://localhost:3000](http://localhost:3000)

### 3. Build for Production

```bash
npm run build
```

## User Flow

1. **Landing Page**: Introduction and feature overview
2. **Login**: Authentication
3. **Overview Dashboard**: Project statistics and recent activity
4. **Upload Drawing**: Drag-and-drop file upload with analysis workflow
5. **QTO**: View extracted quantities with confidence scores
6. **Cost Intelligence**: Cost estimation with uncertainty bands
7. **Schedule**: Phase-wise project timeline
8. **Validation**: Quality checks and confidence scoring
9. **Optimization**: Cost-saving suggestions
10. **Suppliers**: Supplier directory and comparison
11. **Procurement**: RFQ generation
12. **Reports**: Export documentation

## Design Principles

- **Enterprise-grade**: Professional, reliable interface
- **Engineering precision**: Clear data hierarchy and validation
- **Explainability**: Transparent AI outputs with confidence scores
- **Human-in-the-loop**: Review and approval workflows
- **Compliance-ready**: Export standardized reports

## Component Usage

### Button
```jsx
<Button variant="primary" size="md">Click Me</Button>
<Button variant="outline">Secondary Action</Button>
```

### Card
```jsx
<Card title="Card Title" action={<Button>Action</Button>}>
  Content here
</Card>
```

### Badge
```jsx
<Badge variant="success">Completed</Badge>
<Badge variant="warning">In Progress</Badge>
```

### Table
```jsx
<Table 
  columns={[
    { header: 'Name', accessor: 'name' },
    { header: 'Value', accessor: 'value' }
  ]}
  data={data}
/>
```

## Future Enhancements

- Backend API integration
- Real-time collaboration
- Advanced analytics dashboard
- Mobile responsive design
- Multi-language support
- Role-based access control

## License

Proprietary - Enterprise Construction Intelligence Platform

---

Built with ❤️ for the construction industry
