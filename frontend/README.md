# Solaris Energy Operator Assistant - Frontend

Next.js frontend application for the Solaris Energy Operator Assistant chatbot.

## Design System

This frontend is styled to match Solaris Energy's brand guidelines:
- **Font**: Source Sans Pro
- **Colors**:
  - Primary: #0066CC (Energy blue)
  - Secondary: #00CC66 (Green accent)
  - Background: #EEEEEE (Light gray)
  - Text: #171616 (Dark gray)
- **Style**: Professional, clean, energy industry-focused

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp .env.local.example .env.local
```

3. Configure API endpoint in `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
NEXT_PUBLIC_API_KEY=your-api-key-here
```

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Features

- **Chat Interface**: Clean, professional chat UI matching Solaris Energy branding
- **Session Management**: Automatic session handling with localStorage persistence
- **Citations**: Source citations displayed with relevance scores
- **Confidence Indicators**: Visual confidence scores for responses
- **Turbine Model Detection**: Automatically detects and displays turbine model
- **Responsive Design**: Works on desktop and mobile devices

## Components

- `ChatWindow`: Main chat container with session management
- `MessageBubble`: Individual message display with citations and metadata
- `InputBox`: Text input with send button

## API Integration

The frontend integrates with the API Gateway endpoints:
- `POST /chat` - Send query and receive response
- `GET /chat/{session_id}` - Retrieve conversation history
- `DELETE /chat/{session_id}` - Clear session

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to S3

The frontend can be deployed to the S3 bucket created by the StorageStack:

```bash
# Build the application
npm run build

# Deploy to S3 (bucket name from CDK output)
aws s3 sync out/ s3://solaris-poc-frontend-ACCOUNT-REGION/ --delete
```

### Environment Variables

Set the following environment variables before building:

- `NEXT_PUBLIC_API_URL`: API Gateway endpoint URL
- `NEXT_PUBLIC_API_KEY`: API Gateway API key (optional)

## Development

```bash
# Run development server
npm run dev

# Run linting
npm run lint

# Type checking
npm run type-check
```

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Source Sans Pro** - Font family (matching Solaris Energy brand)
