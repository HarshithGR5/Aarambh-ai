'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { toast } from 'sonner';
import { Brain, ArrowRight, Smartphone, KeyRound } from 'lucide-react';
import Link from 'next/link';

const phoneSchema = z.object({ phone: z.string().min(10, 'Enter valid phone number').max(15) });
const otpSchema = z.object({ otp: z.string().min(4, 'Enter OTP').max(6) });

type PhoneForm = z.infer<typeof phoneSchema>;
type OtpForm = z.infer<typeof otpSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const phoneForm = useForm<PhoneForm>({ resolver: zodResolver(phoneSchema) });
  const otpForm = useForm<OtpForm>({ resolver: zodResolver(otpSchema) });

  const onPhoneSubmit = async (data: PhoneForm) => {
    setLoading(true);
    try {
      const res = await authApi.requestOtp(data.phone);
      setPhone(data.phone);
      if (res.data.otp) setDevOtp(res.data.otp);
      setStep('otp');
      toast.success('OTP sent successfully');
    } catch {
      toast.error('Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onOtpSubmit = async (data: OtpForm) => {
    setLoading(true);
    try {
      const res = await authApi.verifyOtp(phone, data.otp);
      setAuth(res.data.user, res.data.access_token);
      toast.success(`Welcome, ${res.data.user.name}!`);
      const role = res.data.user.role;
      if (role === 'AWW') router.replace('/home');
      else router.replace('/overview');
    } catch {
      toast.error('Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-950 via-brand-900 to-brand-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="h-16 w-16 rounded-2xl bg-white/10 flex items-center justify-center mb-4 backdrop-blur-sm border border-white/20">
            <Brain className="h-9 w-9 text-white" />
          </div>
          <h1 className="text-2xl font-display font-bold text-white">Aarambh AI</h1>
          <p className="text-brand-300 text-sm mt-1">Developmental Digital Twin Platform</p>
        </div>

        <Card className="border-0 shadow-2xl shadow-brand-900/50 bg-white">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl font-display">
              {step === 'phone' ? 'Sign In' : 'Verify OTP'}
            </CardTitle>
            <CardDescription>
              {step === 'phone'
                ? 'Enter your registered phone number'
                : `OTP sent to +${phone}`}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {step === 'phone' ? (
              <form onSubmit={phoneForm.handleSubmit(onPhoneSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <div className="relative">
                    <Smartphone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="9876543210"
                      className="pl-10"
                      {...phoneForm.register('phone')}
                    />
                  </div>
                  {phoneForm.formState.errors.phone && (
                    <p className="text-xs text-destructive">{phoneForm.formState.errors.phone.message}</p>
                  )}
                </div>
                <Button type="submit" className="w-full" size="lg" loading={loading}>
                  Send OTP <ArrowRight className="h-4 w-4" />
                </Button>
              </form>
            ) : (
              <form onSubmit={otpForm.handleSubmit(onOtpSubmit)} className="space-y-4">
                {devOtp && (
                  <Badge variant="amber" className="w-full justify-center py-2 text-sm font-mono">
                    Dev OTP: {devOtp}
                  </Badge>
                )}
                <div className="space-y-2">
                  <Label htmlFor="otp">One-Time Password</Label>
                  <div className="relative">
                    <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="otp"
                      type="text"
                      inputMode="numeric"
                      placeholder="••••••"
                      maxLength={6}
                      className="pl-10 text-lg tracking-[0.5em] text-center font-mono"
                      {...otpForm.register('otp')}
                    />
                  </div>
                  {otpForm.formState.errors.otp && (
                    <p className="text-xs text-destructive">{otpForm.formState.errors.otp.message}</p>
                  )}
                </div>
                <Button type="submit" className="w-full" size="lg" loading={loading}>
                  Verify & Sign In <ArrowRight className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full text-sm"
                  onClick={() => { setStep('phone'); setDevOtp(null); }}
                >
                  ← Change Phone Number
                </Button>
              </form>
            )}

            <div className="text-center text-xs text-muted-foreground pt-2 border-t">
              Aarambh AI · ICDS / RBSK Platform
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-brand-400 text-xs mt-6">
          <Link href="/" className="hover:text-white transition-colors">← Back to home</Link>
        </p>
      </div>
    </div>
  );
}
