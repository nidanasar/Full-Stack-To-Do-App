---
description: Implement controlled forms with validation, error handling, and loading states in React.
---

# Skill: Form Handling

## Purpose
Provide patterns for building forms with validation, error states, and loading indicators for authentication and task management.

## Stack Context
- **Frontend**: Next.js + React
- **Validation**: Client-side with HTML5 + custom
- **State**: useState for form data and errors

## Core Pattern

```typescript
"use client";

import { useState, FormEvent } from "react";

interface FormState<T> {
  data: T;
  errors: Partial<Record<keyof T, string>>;
  isSubmitting: boolean;
  submitError: string | null;
}
```

## Authentication Form

### Login/Register Form
```typescript
// components/auth-form.tsx
"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";

interface AuthFormProps {
  mode: "login" | "register";
}

interface Credentials {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const { signIn, signUp } = useAuth();

  const [credentials, setCredentials] = useState<Credentials>({
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): boolean {
    const newErrors: FormErrors = {};

    // Email validation
    if (!credentials.email) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(credentials.email)) {
      newErrors.email = "Invalid email format";
    }

    // Password validation
    if (!credentials.password) {
      newErrors.password = "Password is required";
    } else if (credentials.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);

    if (!validate()) return;

    setIsSubmitting(true);

    try {
      if (mode === "login") {
        await signIn(credentials.email, credentials.password);
      } else {
        await signUp(credentials.email, credentials.password);
      }
      router.push("/");
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : "An error occurred"
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleChange(field: keyof Credentials, value: string) {
    setCredentials((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={credentials.email}
          onChange={(e) => handleChange("email", e.target.value)}
          className={`mt-1 block w-full rounded border p-2 ${
            errors.email ? "border-red-500" : "border-gray-300"
          }`}
          disabled={isSubmitting}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-500">{errors.email}</p>
        )}
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={credentials.password}
          onChange={(e) => handleChange("password", e.target.value)}
          className={`mt-1 block w-full rounded border p-2 ${
            errors.password ? "border-red-500" : "border-gray-300"
          }`}
          disabled={isSubmitting}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-500">{errors.password}</p>
        )}
      </div>

      {/* Submit Error */}
      {submitError && (
        <div className="rounded bg-red-50 p-3 text-red-500">
          {submitError}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded bg-blue-600 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting
          ? "Please wait..."
          : mode === "login"
          ? "Sign In"
          : "Create Account"}
      </button>
    </form>
  );
}
```

## Task Form

### Create/Edit Task Form
```typescript
// components/task-form.tsx
"use client";

import { useState, FormEvent } from "react";
import { Task } from "@/types";

interface TaskFormProps {
  initialData?: Task;
  onSubmit: (data: { title: string; description: string }) => Promise<void>;
  onCancel?: () => void;
}

interface FormData {
  title: string;
  description: string;
}

interface FormErrors {
  title?: string;
}

export function TaskForm({ initialData, onSubmit, onCancel }: TaskFormProps) {
  const [formData, setFormData] = useState<FormData>({
    title: initialData?.title || "",
    description: initialData?.description || "",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): boolean {
    const newErrors: FormErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    if (!validate()) return;

    setIsSubmitting(true);

    try {
      await onSubmit({
        title: formData.title.trim(),
        description: formData.description.trim(),
      });
      // Reset form after successful create
      if (!initialData) {
        setFormData({ title: "", description: "" });
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title Field */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium">
          Title *
        </label>
        <input
          id="title"
          type="text"
          value={formData.title}
          onChange={(e) => {
            setFormData((prev) => ({ ...prev, title: e.target.value }));
            if (errors.title) setErrors({});
          }}
          className={`mt-1 block w-full rounded border p-2 ${
            errors.title ? "border-red-500" : "border-gray-300"
          }`}
          disabled={isSubmitting}
          placeholder="What needs to be done?"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-500">{errors.title}</p>
        )}
      </div>

      {/* Description Field */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium">
          Description
        </label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, description: e.target.value }))
          }
          className="mt-1 block w-full rounded border border-gray-300 p-2"
          disabled={isSubmitting}
          rows={3}
          placeholder="Add details (optional)"
        />
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting
            ? "Saving..."
            : initialData
            ? "Update Task"
            : "Add Task"}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="rounded border px-4 py-2 hover:bg-gray-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
```

## Reusable Form Hook

```typescript
// hooks/use-form.ts
"use client";

import { useState, useCallback, ChangeEvent } from "react";

interface UseFormOptions<T> {
  initialValues: T;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
  onSubmit: (values: T) => Promise<void>;
}

export function useForm<T extends Record<string, unknown>>({
  initialValues,
  validate,
  onSubmit,
}: UseFormOptions<T>) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleChange = useCallback(
    (field: keyof T) =>
      (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const value = e.target.value;
        setValues((prev) => ({ ...prev, [field]: value }));
        if (errors[field]) {
          setErrors((prev) => ({ ...prev, [field]: undefined }));
        }
      },
    [errors]
  );

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setSubmitError(null);

      // Validate
      if (validate) {
        const validationErrors = validate(values);
        if (Object.keys(validationErrors).length > 0) {
          setErrors(validationErrors);
          return;
        }
      }

      setIsSubmitting(true);

      try {
        await onSubmit(values);
      } catch (err) {
        setSubmitError(
          err instanceof Error ? err.message : "An error occurred"
        );
      } finally {
        setIsSubmitting(false);
      }
    },
    [values, validate, onSubmit]
  );

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setSubmitError(null);
  }, [initialValues]);

  return {
    values,
    errors,
    isSubmitting,
    submitError,
    handleChange,
    handleSubmit,
    reset,
    setValues,
  };
}
```

### Usage with Hook
```typescript
// components/quick-task-form.tsx
"use client";

import { useForm } from "@/hooks/use-form";

export function QuickTaskForm({ onAdd }: { onAdd: (title: string) => Promise<void> }) {
  const { values, errors, isSubmitting, handleChange, handleSubmit } = useForm({
    initialValues: { title: "" },
    validate: (v) => (!v.title.trim() ? { title: "Required" } : {}),
    onSubmit: async (v) => {
      await onAdd(v.title);
    },
  });

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        value={values.title}
        onChange={handleChange("title")}
        placeholder="Add a task..."
        className="flex-1 rounded border p-2"
      />
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "..." : "Add"}
      </button>
    </form>
  );
}
```

## Validation Rules

| Field | Rules |
|-------|-------|
| Email | Required, valid format |
| Password | Required, min 8 chars |
| Task title | Required, not empty |
| Task description | Optional |

## Checklist
- [ ] Forms are controlled (useState for values)
- [ ] Validation runs before submit
- [ ] Errors display below fields
- [ ] Loading state disables inputs
- [ ] Submit errors shown prominently
- [ ] Fields clear errors on change
- [ ] Accessible labels with htmlFor
