import LoginForm from "./LoginForm";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md p-4 space-y-4 bg-white rounded-lg shadow-lg">
        <h1 className="text-2xl font-semibold text-center">Login</h1>
        <LoginForm />
      </div>
    </div>
  );
}
