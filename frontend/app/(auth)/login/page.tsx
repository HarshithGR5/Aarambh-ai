'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { toast } from 'sonner';
import {
  Brain, ArrowRight, Smartphone, KeyRound, ChevronDown,
  Users, Building2, Stethoscope, GraduationCap, Star,
} from 'lucide-react';
import Link from 'next/link';

const phoneSchema = z.object({ phone: z.string().min(10, 'Enter a valid 10-digit phone number').max(15) });
const otpSchema   = z.object({ otp:   z.string().min(4, 'Enter your OTP').max(6) });

type PhoneForm = z.infer<typeof phoneSchema>;
type OtpForm   = z.infer<typeof otpSchema>;

const ROLE_REDIRECT: Record<string, string> = {
  AWW:           '/home',
  CDPO:          '/overview',
  HEALTH_WORKER: '/referrals',
  STATE_OFFICER: '/district',
  ADMIN:         '/overview',
};

const demoAccounts = [
  { role: 'AWW',           label: 'Anganwadi Worker',  phone: '9876543001', icon: Users,         color: 'text-violet-600 bg-violet-50' },
  { role: 'CDPO',          label: 'CDPO Officer',       phone: '9876543002', icon: Building2,     color: 'text-blue-600 bg-blue-50' },
  { role: 'HEALTH_WORKER', label: 'RBSK Health Worker', phone: '9876543003', icon: Stethoscope,   color: 'text-green-600 bg-green-50' },
  { role: 'STATE_OFFICER', label: 'State Officer',      phone: '9876543004', icon: GraduationCap, color: 'text-amber-600 bg-amber-50' },
  { role: 'ADMIN',         label: 'Administrator',      phone: '9876543005', icon: Star,          color: 'text-rose-600 bg-rose-50' },
];

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [step, setStep]         = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [showDemo, setShowDemo] = useState(false);
  const [devOtp, setDevOtp]     = useState('');

  const phoneForm = useForm<PhoneForm>({ resolver: zodResolver(phoneSchema) });
  const otpForm   = useForm<OtpForm>({ resolver: zodResolver(otpSchema) });

  const onPhoneSubmit = async (data: PhoneForm) => {
    setLoading(true);
    try {
      const res = await authApi.requestOtp(data.phone);
      setPhone(data.phone);
      setStep('otp');
      if (res.data?.otp) setDevOtp(res.data.otp);
      toast.success('OTP sent to your phone');
    } catch {
      toast.error('Could not send OTP. Is this number registered?');
    } finally {
      setLoading(false);
    }
  };

  const onOtpSubmit = async (data: OtpForm) => {
    setLoading(true);
    try {
      const res = await authApi.verifyOtp(phone, data.otp);
      setAuth(res.data.user, res.data.access_token);
      const role = res.data.user.role as string;
      toast.success(`Welcome back, ${res.data.user.name}!`);
      router.replace(ROLE_REDIRECT[role] ?? '/overview');
    } catch {
      toast.error('Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (acc: typeof demoAccounts[0]) => {
    phoneForm.setValue('phone', acc.phone);
    setShowDemo(false);
    toast.info(`Filled: ${acc.label} (${acc.phone}). Click Send OTP to continue.`);
  };

  return (
    <div className="min-h-screen flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex flex-col w-[480px] shrink-0 relative bg-gradient-to-br from-slate-950 via-brand-950 to-slate-900 text-white p-10 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,rgba(59,130,246,0.15),transparent)]" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <div className="h-10 w-10 rounded-2xl bg-white/10 border border-white/15 flex items-center justify-center backdrop-blur-sm">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="font-display font-bold text-white leading-none">Aarambh AI</p>
              <p className="text-[11px] text-brand-400 mt-0.5">Developmental Digital Twin Platform</p>
            </div>
          </div>

          <h1 className="text-4xl font-display font-extrabold leading-tight mb-5">
            AI-powered tracking<br />for every child<br />in India.
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed mb-10">
            From Anganwadi workers recording voice observations to state officers analyzing
            district-level heatmaps — one unified platform for India's 158 million children under 6.
          </p>

          <div className="space-y-3">
            {[
              '6-domain Developmental Digital Twin',
              'Voice observations in any Indian language',
              'Automated RBSK / NPPCD referral letters',
              'PDRS risk scoring with GREEN/AMBER/RED',
            ].map(item => (
              <div key={item} className="flex items-center gap-2.5 text-sm text-slate-300">
                <div className="h-5 w-5 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center shrink-0">
                  <div className="h-1.5 w-1.5 rounded-full bg-brand-400" />
                </div>
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 mt-auto pt-10 border-t border-white/10 text-xs text-slate-500">
          ICDS · RBSK · NPPCD · DEIC Aligned · NEP 2020 Domains
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex flex-col items-center justify-center bg-slate-50 px-5 py-12">
        {/* Mobile logo */}
        <div className="lg:hidden flex items-center gap-3 mb-10">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-200">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <div>
            <p className="font-display font-bold text-gray-900 leading-none">Aarambh AI</p>
            <p className="text-[11px] text-gray-400 mt-0.5">Developmental Digital Twin Platform</p>
          </div>
        </div>

        <div className="w-full max-w-sm">
          {/* Step indicator */}
          <div className="flex items-center gap-3 mb-6">
            <div className={`flex items-center gap-1.5 text-sm font-medium ${step === 'phone' ? 'text-brand-600' : 'text-gray-400'}`}>
              <div className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${step === 'phone' ? 'bg-brand-600 text-white' : 'bg-gray-200 text-gray-500'}`}>1</div>
              Phone
            </div>
            <div className="flex-1 h-px bg-gray-200" />
            <div className={`flex items-center gap-1.5 text-sm font-medium ${step === 'otp' ? 'text-brand-600' : 'text-gray-400'}`}>
              <div className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${step === 'otp' ? 'bg-brand-600 text-white' : 'bg-gray-200 text-gray-500'}`}>2</div>
              Verify
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 pt-6 pb-5 border-b border-gray-100">
              <h2 className="text-xl font-display font-bold text-gray-900">
                {step === 'phone' ? 'Sign in to Aarambh AI' : 'Verify your identity'}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {step === 'phone'
                  ? 'Enter your registered mobile number'
                  : `OTP sent to +91-${phone}`}
              </p>
            </div>

            <div className="p-6">
              {step === 'phone' ? (
                <form onSubmit={phoneForm.handleSubmit(onPhoneSubmit)} className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="phone" className="text-sm font-medium text-gray-700">Mobile Number</Label>
                    <div className="relative">
                      <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-sm text-gray-400 pointer-events-none select-none">
                        <Smartphone className="h-4 w-4" />
                        <span className="border-r border-gray-200 pr-1.5">+91</span>
                      </div>
                      <Input
                        id="phone"
                        type="tel"
                        inputMode="numeric"
                        placeholder="9876543210"
                        className="pl-20 h-11 rounded-xl border-gray-200 focus-visible:ring-brand-500"
                        {...phoneForm.register('phone')}
                      />
                    </div>
                    {phoneForm.formState.errors.phone && (
                      <p className="text-xs text-red-500 mt-1">{phoneForm.formState.errors.phone.message}</p>
                    )}
                  </div>
                  <Button type="submit" className="w-full h-11 bg-brand-600 hover:bg-brand-700 rounded-xl font-semibold gap-2" disabled={loading}>
                    {loading
                      ? <span className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      : <><span>Send OTP</span><ArrowRight className="h-4 w-4" /></>
                    }
                  </Button>
                </form>
              ) : (
                <form onSubmit={otpForm.handleSubmit(onOtpSubmit)} className="space-y-4">
                  {devOtp && (
                    <div className="flex items-center justify-between px-3 py-2 bg-amber-50 border border-amber-200 rounded-xl">
                      <span className="text-xs font-medium text-amber-700">Dev OTP</span>
                      <span className="text-lg font-mono font-bold text-amber-800 tracking-[0.3em]">{devOtp}</span>
                    </div>
                  )}
                  <div className="space-y-1.5">
                    <Label htmlFor="otp" className="text-sm font-medium text-gray-700">One-Time Password</Label>
                    <div className="relative">
                      <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="otp"
                        type="text"
                        inputMode="numeric"
                        placeholder="• • • • • •"
                        maxLength={6}
                        className="pl-10 h-11 text-center text-xl tracking-[0.4em] font-mono rounded-xl border-gray-200 focus-visible:ring-brand-500"
                        {...otpForm.register('otp')}
                      />
                    </div>
                    {otpForm.formState.errors.otp && (
                      <p className="text-xs text-red-500 mt-1">{otpForm.formState.errors.otp.message}</p>
                    )}
                  </div>
                  <Button type="submit" className="w-full h-11 bg-brand-600 hover:bg-brand-700 rounded-xl font-semibold gap-2" disabled={loading}>
                    {loading
                      ? <span className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      : <><span>Verify & Sign In</span><ArrowRight className="h-4 w-4" /></>
                    }
                  </Button>
                  <button
                    type="button"
                    onClick={() => { setStep('phone'); otpForm.reset(); }}
                    className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors py-1"
                  >
                    ← Change phone number
                  </button>
                </form>
              )}
            </div>
          </div>

          {/* Demo credentials */}
          <div className="mt-4 border border-dashed border-gray-200 rounded-xl bg-white overflow-hidden">
            <button
              type="button"
              onClick={() => setShowDemo(d => !d)}
              className="w-full flex items-center justify-between px-4 py-3 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <span className="font-medium">Demo accounts (development)</span>
              <ChevronDown className={`h-4 w-4 transition-transform ${showDemo ? 'rotate-180' : ''}`} />
            </button>
            {showDemo && (
              <div className="border-t border-gray-100 p-3 space-y-1.5">
                {demoAccounts.map(acc => (
                  <button
                    key={acc.role}
                    type="button"
                    onClick={() => fillDemo(acc)}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-colors text-left"
                  >
                    <div className={`h-7 w-7 rounded-lg ${acc.color} flex items-center justify-center shrink-0`}>
                      <acc.icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700 leading-tight">{acc.label}</p>
                      <p className="text-xs text-gray-400 font-mono">{acc.phone}</p>
                    </div>
                  </button>
                ))}
                <p className="text-[11px] text-gray-400 px-3 pt-1">OTP is shown in the verify screen after clicking Send OTP</p>
              </div>
            )}
          </div>

          <p className="text-center text-xs text-gray-400 mt-5">
            <Link href="/" className="hover:text-gray-600 transition-colors">← Back to home</Link>
            <span className="mx-2">·</span>
            Aarambh AI · ICDS Platform
          </p>
        </div>
      </div>
    </div>
  );
}
