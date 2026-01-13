# Hackathon Todo

A full-stack todo application for hackathon productivity.

## Features

- User authentication (signup/login)
- Create, read, update, delete tasks
- Filter tasks by status
- Responsive design

## Tech Stack

### Frontend
- React
- TypeScript
- React Router

### Backend
- Node.js
- Express
- Prisma ORM
- SQLite

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackathon-todo

# Install dependencies
npm install

# Set up environment variables
cp backend/.env.example backend/.env

# Run database migrations
cd backend && npm run db:migrate

# Start development servers
npm run dev
```

### Development

```bash
# Run frontend only
cd frontend && npm run dev

# Run backend only
cd backend && npm run dev

# Run both
npm run dev
```

## Project Structure

```
hackathon-todo/
├── specs/          # Project specifications
├── frontend/       # React application
├── backend/        # Express API
└── README.md
```

## API Documentation

See `specs/api/rest-endpoints.md` for full API documentation.

## License

MIT
