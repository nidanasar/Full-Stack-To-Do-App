# Database Schema

## Tables

### users
| Column     | Type      | Constraints          |
|------------|-----------|----------------------|
| id         | UUID      | PRIMARY KEY          |
| email      | VARCHAR   | UNIQUE, NOT NULL     |
| password   | VARCHAR   | NOT NULL             |
| created_at | TIMESTAMP | DEFAULT NOW()        |
| updated_at | TIMESTAMP | DEFAULT NOW()        |

### tasks
| Column      | Type      | Constraints                    |
|-------------|-----------|--------------------------------|
| id          | UUID      | PRIMARY KEY                    |
| user_id     | UUID      | FOREIGN KEY (users.id), NOT NULL |
| title       | VARCHAR   | NOT NULL                       |
| description | TEXT      | NULLABLE                       |
| completed   | BOOLEAN   | DEFAULT FALSE                  |
| created_at  | TIMESTAMP | DEFAULT NOW()                  |
| updated_at  | TIMESTAMP | DEFAULT NOW()                  |

## Indexes
- `users.email` - Unique index for login lookups
- `tasks.user_id` - Index for user's task queries

## Relationships
- User 1:N Tasks (one user has many tasks)
- Task N:1 User (each task belongs to one user)

## Prisma Schema
```prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  tasks     Task[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Task {
  id          String   @id @default(uuid())
  title       String
  description String?
  completed   Boolean  @default(false)
  user        User     @relation(fields: [userId], references: [id])
  userId      String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```
