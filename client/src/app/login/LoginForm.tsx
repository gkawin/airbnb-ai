"use client";

import { useFormState, useFormStatus } from "react-dom";
import { loginFormAction } from "./action";

export default function LoginForm() {
  const [state, formAction] = useFormState(loginFormAction, {
    error: null,
    user: null,
  });
  const { pending } = useFormStatus();

  return (
    <form className="space-y-4" action={formAction}>
      <div className="space-y-1">
        <label htmlFor="email" className="text-sm font-medium">
          Email
        </label>
        <input
          type="email"
          id="email"
          name="email"
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>
      <div className="space-y-1">
        <label htmlFor="password" className="text-sm font-medium">
          Password
        </label>
        <input
          type="password"
          id="password"
          name="password"
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>
      {state.error && <div className="text-red-500 text-sm">{state.error}</div>}
      <button
        type="submit"
        className="btn w-full btn-primary"
        disabled={pending}
      >
        Login
      </button>
    </form>
  );
}
