import { FormEvent, useState } from "react";
import { LockKeyhole, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";

export function AuthScreen() {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "register") {
        await signUp(name, email, password);
      } else {
        await signIn(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-5 py-10">
      <div className="w-full max-w-md rounded-card border border-border bg-panel p-6 shadow-panel">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-card border border-primary/40 bg-primary/15 text-blue-100">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-white">DocuTrust</h1>
            <p className="text-sm text-muted">Enterprise Advanced RAG Platform</p>
          </div>
        </div>

        <div className="mb-5 grid grid-cols-2 rounded-card border border-border bg-white/[0.03] p-1">
          <button
            className={mode === "login" ? "segmented-active" : "segmented"}
            type="button"
            onClick={() => setMode("login")}
          >
            Login
          </button>
          <button
            className={mode === "register" ? "segmented-active" : "segmented"}
            type="button"
            onClick={() => setMode("register")}
          >
            Register
          </button>
        </div>

        <form className="space-y-4" onSubmit={submit}>
          {mode === "register" ? (
            <label className="field-label">
              Name
              <Input value={name} onChange={(event) => setName(event.target.value)} />
            </label>
          ) : null}
          <label className="field-label">
            Email
            <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label className="field-label">
            Password
            <Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          {error ? <p className="rounded-card border border-danger/40 bg-danger/10 p-3 text-sm text-red-100">{error}</p> : null}
          <Button className="w-full" loading={loading}>
            <LockKeyhole className="h-4 w-4" />
            {mode === "register" ? "Create Account" : "Sign In"}
          </Button>
        </form>
      </div>
    </main>
  );
}
