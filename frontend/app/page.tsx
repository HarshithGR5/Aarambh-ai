'use client';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Brain, Mic, BarChart3, Shield, ArrowRight, CheckCircle2, Sparkles, Globe2, Users, Activity } from 'lucide-react';

const features = [
  { icon: Brain, title: 'Developmental Digital Twin', desc: 'AI-powered living profile tracking all 6 development domains continuously', color: 'bg-blue-50 text-blue-600' },
  { icon: Mic, title: 'Voice Observation Engine', desc: 'Record observations in any Indian language — AI extracts structured insights', color: 'bg-purple-50 text-purple-600' },
  { icon: BarChart3, title: 'PDRS Risk Scoring', desc: 'Predictive 0–100 risk score with GREEN/AMBER/RED classification', color: 'bg-green-50 text-green-600' },
  { icon: Shield, title: 'Referral Automation', desc: 'One-tap referral letters with government scheme matching (RBSK, NPPCD)', color: 'bg-amber-50 text-amber-600' },
];

const stats = [
  { value: '1.36M', label: 'Anganwadi Centres', icon: Globe2 },
  { value: '158M', label: 'Children Under 6', icon: Users },
  { value: '6', label: 'Development Domains', icon: Activity },
  { value: 'AI', label: 'Powered Analysis', icon: Sparkles },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-950 via-brand-900 to-brand-800 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/10 backdrop-blur-md bg-brand-950/80">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-white/10 flex items-center justify-center">
              <Brain className="h-5 w-5 text-brand-300" />
            </div>
            <span className="font-display font-bold text-lg text-white">Aarambh AI</span>
          </div>
          <Link href="/login">
            <Button variant="outline" className="border-white/20 bg-white/5 text-white hover:bg-white/10" size="sm">
              Sign In <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20 text-center">
        <Badge className="bg-brand-800/60 border-brand-600/50 text-brand-200 mb-6 backdrop-blur-sm">
          <Sparkles className="h-3 w-3 mr-1" /> India's First Developmental Digital Twin Platform
        </Badge>
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-display font-bold tracking-tight leading-none mb-6">
          Every Child{' '}
          <span className="bg-gradient-to-r from-brand-300 to-teal-300 bg-clip-text text-transparent">
            Seen.
          </span>
          <br />
          Every Child{' '}
          <span className="bg-gradient-to-r from-teal-300 to-brand-300 bg-clip-text text-transparent">
            Supported.
          </span>
        </h1>
        <p className="text-xl text-brand-200 max-w-2xl mx-auto mb-10 leading-relaxed">
          AI-powered developmental tracking for Anganwadi workers across India. 
          Catch delays early. Automate referrals. Transform child outcomes.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/login">
            <Button size="xl" className="bg-white text-brand-900 hover:bg-brand-50 font-bold shadow-2xl shadow-brand-900/50 gap-2">
              Get Started <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
          <Button size="xl" variant="outline" className="border-white/20 bg-white/5 text-white hover:bg-white/10">
            View API Docs
          </Button>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-6xl mx-auto px-6 pb-20">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map(({ value, label, icon: Icon }) => (
            <div key={label} className="bg-white/5 border border-white/10 rounded-2xl p-5 text-center backdrop-blur-sm">
              <Icon className="h-5 w-5 text-brand-300 mx-auto mb-2" />
              <div className="text-2xl font-display font-bold text-white">{value}</div>
              <div className="text-sm text-brand-300 mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <h2 className="text-3xl font-display font-bold text-center mb-12 text-white">
          Built for India's Frontline
        </h2>
        <div className="grid sm:grid-cols-2 gap-5">
          {features.map(({ icon: Icon, title, desc, color }) => (
            <div key={title} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm hover:bg-white/8 transition-colors">
              <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl mb-4 ${color}`}>
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="font-semibold text-white text-lg mb-2">{title}</h3>
              <p className="text-brand-300 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-white/10 bg-white/5">
        <div className="max-w-6xl mx-auto px-6 py-16 text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Ready to transform child outcomes?</h2>
          <p className="text-brand-300 mb-8">Join Anganwadi workers across Karnataka using Aarambh AI</p>
          <div className="flex flex-col items-center gap-3">
            <Link href="/login">
              <Button size="xl" className="bg-white text-brand-900 hover:bg-brand-50 font-bold gap-2">
                Start Using Aarambh AI <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <div className="flex items-center gap-2 text-sm text-brand-400">
              <CheckCircle2 className="h-4 w-4 text-green-400" /> Free for Anganwadi Workers
              <span className="mx-2">·</span>
              <CheckCircle2 className="h-4 w-4 text-green-400" /> No Setup Required
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
