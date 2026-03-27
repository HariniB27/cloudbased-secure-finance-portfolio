import { useState } from "react";
import { Link } from "react-router-dom";
import { Loader2, TrendingUp } from "lucide-react";
import { forgotPassword } from "@/lib/api";
import { getRecaptchaToken } from "@/lib/recaptcha";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const recaptchaToken = await getRecaptchaToken("forgot_password");
      await forgotPassword(email, recaptchaToken);
      toast({
        title: "Request submitted",
        description: "If this account exists, a reset link has been sent.",
      });
    } catch (err: any) {
      toast({
        title: "Request failed",
        description: err.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <TrendingUp className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Forgot Password</h1>
          </div>
          <p className="text-muted-foreground">Enter your email to receive a reset link</p>
        </div>
        <div className="card-elevated p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Send Reset Link
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-6">
            Back to{" "}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
