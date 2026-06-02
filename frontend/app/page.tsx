'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Brain, Mic, BarChart3, Shield, ArrowRight, ChevronRight,
  Sparkles, Globe2, Users, Activity, CheckCircle2,
  Stethoscope, Building2, GraduationCap, Star, Zap,
} from 'lucide-react';

const roles = [
  {
    icon: Users,
    label: 'Anganwadi Worker',
    short: 'AWW',
    color: 'from-violet-500 to-purple-600',
    bg: 'bg-violet-50',
    border: 'border-violet-200',
    textColor: 'text-violet-700',
    desc: 'Record voice observations, track milestones, mark attendance, generate referrals',
    access: 'Mobile-optimized app · Hindi/Kannada/Telugu support',
  },
  {
    icon: Building2,
    label: 'CDPO Officer',
    short: 'CDPO',
    color: 'from-blue-500 to-indigo-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    textColor: 'text-blue-700',
    desc: 'Monitor all AWCs in your block, review risk distributions, manage referrals',
    access: 'Block-level dashboard · AWC performance reports',
  },
  {
    icon: Stethoscope,
    label: 'RBSK Health Worker',
    short: 'HEALTH',
    color: 'from-green-500 to-emerald-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
    textColor: 'text-green-700',
    desc: 'View referred children, track health outcomes, coordinate specialist visits',
    access: 'Referral tracking · Child health records',
  },
  {
    icon: GraduationCap,
    label: 'State Officer',
    short: 'STATE',
    color: 'from-amber-500 to-orange-600',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    textColor: 'text-amber-700',
    desc: 'District-level heatmaps, aggregate analytics, program performance',
    access: 'District analytics · Policy reporting',
  },
  {
    icon: Star,
    label: 'Administrator',
    short: 'ADMIN',
    color: 'from-rose-500 to-pink-600',
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    textColor: 'text-rose-700',
    desc: 'Full system access — user management, scheme database, master data',
    access: 'Full system control · User & scheme management',
  },
];

const features = [
  {
    icon: Brain,
    title: 'Developmental Digital Twin',
    desc: 'A living AI model of each child tracking all 6 NEP 2020 domains — Motor, Cognitive, Language, Social-Emotional, Aesthetic, and Wellbeing.',
    badge: 'Core Innovation',
    badgeColor: 'bg-violet-100 text-violet-700',
  },
  {
    icon: Mic,
    title: 'Voice Observation Engine',
    desc: 'AWW speaks in Kannada, Hindi, or any Indian language. AI transcribes, extracts developmental markers, and classifies them — no typing needed.',
    badge: 'Multilingual AI',
    badgeColor: 'bg-blue-100 text-blue-700',
  },
  {
    icon: BarChart3,
    title: 'PDRS Risk Scoring',
    desc: 'Predictive Developmental Risk Score 0–100 with GREEN/AMBER/RED classification. Aggregated at AWC, block, and district level.',
    badge: 'Predictive ML',
    badgeColor: 'bg-green-100 text-green-700',
  },
  {
    icon: Shield,
    title: 'Smart Referral System',
    desc: 'One-tap government scheme matching (RBSK, NPPCD, DEIC). Auto-generates pre-filled referral letters with NLP. Tracks outcomes end-to-end.',
    badge: 'Automated',
    badgeColor: 'bg-amber-100 text-amber-700',
  },
];

const stats = [
  { value: '1.36M', label: 'Anganwadi Centres', sub: 'across India', icon: Globe2 },
  { value: '158M',  label: 'Children Under 6',  sub: 'target beneficiaries', icon: Users },
  { value: '6',     label: 'Development Domains', sub: 'per NEP 2020', icon: Activity },
  { value: '22+',   label: 'Indian Languages',  sub: 'voice input support', icon: Sparkles },
];

export default function LandingPage() {
  const [activeRole, setActiveRole] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setActiveRole(r => (r + 1) % roles.length), 3500);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="min-h-screen bg-white text-gray-900 overflow-x-hidden">
      {/* Nav */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-xl border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-5 h-15 flex items-center justify-between py-3">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center shadow-md shadow-brand-200">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-display font-bold text-gray-900 text-base leading-none">Aarambh AI</span>
              <span className="block text-[10px] text-gray-400 leading-none mt-0.5">by ICDS Digital</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a href="/api/v1/docs" target="_blank" className="hidden sm:block text-sm text-gray-500 hover:text-gray-800 transition-colors font-medium">
              API Docs
            </a>
            <Link href="/login">
              <Button size="sm" className="bg-brand-600 hover:bg-brand-700 text-white rounded-xl shadow-sm shadow-brand-200 gap-1.5">
                Sign In <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-950 via-brand-950 to-slate-900 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(59,130,246,0.15),transparent)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_50%_at_80%_80%,rgba(139,92,246,0.08),transparent)]" />

        <div className="relative max-w-6xl mx-auto px-5 pt-20 pb-24 text-center">
          <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 text-sm text-brand-300 mb-8 backdrop-blur-sm">
            <Zap className="h-3.5 w-3.5 text-brand-400" />
            India's First Developmental Digital Twin Platform
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl font-display font-extrabold tracking-tight leading-[1.05] mb-7">
            Every Child{' '}
            <span className="bg-gradient-to-r from-brand-300 via-blue-300 to-teal-300 bg-clip-text text-transparent">Seen.</span>
            <br />
            Every Child{' '}
            <span className="bg-gradient-to-r from-teal-300 via-brand-300 to-violet-300 bg-clip-text text-transparent">Supported.</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            AI-powered developmental tracking for India's 1.36 million Anganwadi workers.
            Catch delays early. Automate referrals. Transform child outcomes.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center mb-16">
            <Link href="/login">
              <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-50 font-bold shadow-2xl shadow-black/20 gap-2 rounded-xl px-8">
                Get Started <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <a href="/api/v1/docs" target="_blank">
              <Button size="lg" variant="outline" className="border-white/15 bg-white/5 text-white hover:bg-white/10 rounded-xl backdrop-blur-sm">
                View API Documentation
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto">
            {stats.map(({ value, label, sub, icon: Icon }) => (
              <div key={label} className="bg-white/5 border border-white/8 rounded-2xl p-4 text-center backdrop-blur-sm">
                <Icon className="h-4 w-4 text-brand-400 mx-auto mb-2 opacity-80" />
                <div className="text-2xl font-display font-extrabold text-white">{value}</div>
                <div className="text-xs font-semibold text-brand-300 mt-0.5">{label}</div>
                <div className="text-[11px] text-slate-500 mt-0.5">{sub}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Wave divider */}
        <div className="absolute bottom-0 left-0 right-0 h-12 bg-white" style={{ clipPath: 'ellipse(60% 100% at 50% 100%)' }} />
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-5 py-20">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-1.5 bg-brand-50 text-brand-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-4">
            <Sparkles className="h-3.5 w-3.5" /> Core Capabilities
          </div>
          <h2 className="text-3xl sm:text-4xl font-display font-extrabold text-gray-900 mb-4">Built for India's Frontline</h2>
          <p className="text-gray-500 max-w-xl mx-auto text-base">
            Purpose-built for Anganwadi workers, not retrofitted from clinical tools designed for hospitals.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-5">
          {features.map(({ icon: Icon, title, desc, badge, badgeColor }) => (
            <div key={title} className="group relative bg-white border border-gray-100 rounded-2xl p-6 hover:border-brand-200 hover:shadow-lg hover:shadow-brand-50 transition-all duration-200">
              <div className="flex items-start gap-4 mb-3">
                <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-brand-50 to-brand-100 flex items-center justify-center shrink-0 group-hover:from-brand-100 group-hover:to-brand-200 transition-colors">
                  <Icon className="h-5 w-5 text-brand-700" />
                </div>
                <div>
                  <span className={`inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full mb-1 ${badgeColor}`}>{badge}</span>
                  <h3 className="font-display font-bold text-gray-900 text-base leading-tight">{title}</h3>
                </div>
              </div>
              <p className="text-gray-500 text-sm leading-relaxed pl-15">{desc}</p>
              <div className="absolute bottom-5 right-5 opacity-0 group-hover:opacity-100 transition-opacity">
                <ChevronRight className="h-4 w-4 text-brand-400" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Roles */}
      <section className="bg-slate-50 border-y border-slate-100">
        <div className="max-w-6xl mx-auto px-5 py-20">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-1.5 bg-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-4">
              <Users className="h-3.5 w-3.5" /> 5 User Roles
            </div>
            <h2 className="text-3xl sm:text-4xl font-display font-extrabold text-gray-900 mb-4">One Platform, Every Stakeholder</h2>
            <p className="text-gray-500 max-w-xl mx-auto text-sm">
              From field workers to state officers — each role sees a tailored view built for their context.
            </p>
          </div>

          <div className="flex flex-col lg:flex-row gap-6 items-start">
            <div className="w-full lg:w-64 space-y-2 shrink-0">
              {roles.map((role, i) => (
                <button
                  key={role.short}
                  onClick={() => setActiveRole(i)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all border ${
                    activeRole === i
                      ? `${role.bg} ${role.border} shadow-sm`
                      : 'bg-white border-slate-100 hover:border-slate-200'
                  }`}
                >
                  <div className={`h-8 w-8 rounded-lg bg-gradient-to-br ${role.color} flex items-center justify-center shrink-0`}>
                    <role.icon className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className={`text-sm font-semibold ${activeRole === i ? role.textColor : 'text-gray-700'}`}>{role.label}</p>
                    <p className="text-xs text-gray-400">{role.short}</p>
                  </div>
                </button>
              ))}
            </div>

            <div className={`flex-1 ${roles[activeRole].bg} border ${roles[activeRole].border} rounded-2xl p-8`}>
              <div className={`inline-flex items-center justify-center h-12 w-12 rounded-2xl bg-gradient-to-br ${roles[activeRole].color} mb-5`}>
                {(() => { const Icon = roles[activeRole].icon; return <Icon className="h-6 w-6 text-white" />; })()}
              </div>
              <h3 className={`text-xl font-display font-bold mb-2 ${roles[activeRole].textColor}`}>{roles[activeRole].label}</h3>
              <p className="text-gray-700 text-sm leading-relaxed mb-5">{roles[activeRole].desc}</p>
              <div className="bg-white/60 rounded-xl px-4 py-3 text-xs text-gray-500 font-medium border border-white/80">
                <span className={`font-semibold ${roles[activeRole].textColor}`}>Platform access: </span>
                {roles[activeRole].access}
              </div>
              <div className="mt-5">
                <Link href="/login">
                  <Button size="sm" className={`bg-gradient-to-r ${roles[activeRole].color} text-white border-0 rounded-xl shadow-sm gap-1.5`}>
                    Sign in as {roles[activeRole].short} <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative bg-gradient-to-br from-brand-900 via-brand-800 to-slate-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_80%_at_50%_50%,rgba(59,130,246,0.12),transparent)]" />
        <div className="relative max-w-3xl mx-auto px-5 py-20 text-center">
          <h2 className="text-3xl sm:text-4xl font-display font-extrabold mb-4">Ready to transform child outcomes?</h2>
          <p className="text-brand-300 mb-8 text-base">
            Join Anganwadi workers, CDPO officers, and state administrators across India using Aarambh AI.
          </p>
          <Link href="/login">
            <Button size="lg" className="bg-white text-brand-900 hover:bg-brand-50 font-bold gap-2 rounded-xl px-8 shadow-2xl">
              Start Using Aarambh AI <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 mt-7 text-sm text-brand-400">
            {['Free for AWW Workers', 'ICDS Aligned', 'NEP 2020 Domains', 'Offline Ready'].map(item => (
              <span key={item} className="flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-brand-500" /> {item}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-5 py-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center">
              <Brain className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="font-semibold text-gray-600">Aarambh AI</span>
            <span>· India's ICDS Developmental Platform</span>
          </div>
          <div className="flex items-center gap-4">
            <a href="/api/v1/docs" target="_blank" className="hover:text-gray-600 transition-colors">API Docs</a>
            <span>·</span>
            <span>RBSK · NPPCD · DEIC Aligned</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
