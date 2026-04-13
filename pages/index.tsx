import React, { useState } from 'react';
import Head from 'next/head';
import { Mail, Send, Loader2, Sparkles, BookOpen, Quote, Target, CheckCircle } from 'lucide-react';

export default function GrowwPulseNewsletter() {
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");

  const runAnalysis = async () => {
    if (!email || !name) {
      alert("Please provide both name and email.");
      return;
    }
    
    setLoading(true);
    setComplete(false);
    setStatus("Curating weekly insights...");
    
    try {
      const response = await fetch('/api/pulse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setStatus("Newsletter delivered!");
        setComplete(true);
      } else {
        setStatus(`Delivery Failed: ${result.message || 'Check Environment Variables'}`);
      }
    } catch (err) {
      setStatus("Connection error to intelligence engine.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fdfaf6] text-[#1a1a1a] p-6 lg:p-12 font-serif selection:bg-[#00d09c]/30">
      <Head>
        <title>The GROWW Pulse | Weekly Editorial</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
      </Head>
      
      <div className="max-w-3xl mx-auto bg-white border border-[#e5e1da] shadow-sm rounded-sm p-4 lg:p-16">
        {/* Masthead */}
        <header className="text-center border-b-2 border-[#1a1a1a] pb-8 mb-12">
          <div className="flex justify-between items-center text-[10px] uppercase tracking-[0.2em] font-sans font-bold text-slate-400 mb-6">
            <span>Volume I • Issue IV</span>
            <span>{new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
          </div>
          <h1 className="text-6xl lg:text-8xl font-black font-['Playfair_Display'] tracking-tighter mb-4 italic">
            Groww <span className="text-[#00d09c]">Pulse.</span>
          </h1>
          <p className="text-xl font-medium font-sans text-slate-500 uppercase tracking-widest">Weekly Intelligence & User Sentiment Report</p>
        </header>

        {/* Introduction */}
        <div className="grid lg:grid-cols-3 gap-12 mb-12">
          <div className="lg:col-span-2 font-sans leading-relaxed text-slate-600">
            <p className="mb-4 first-letter:text-5xl first-letter:font-bold first-letter:mr-3 first-letter:float-left first-letter:text-[#1a1a1a]">
              The Groww Pulse is a curated briefing designed for teams who prioritize user feedback. By leveraging advanced LLM analysis, we transform raw Play Store noise into strategic editorial insights.
            </p>
            <p>
              Each report identifies exactly five recurring themes, synthesizes actionable steps, and highlights the voices that matter most—your users.
            </p>
          </div>
          <div className="bg-[#f8f6f2] p-6 rounded-sm border border-[#e5e1da] transform rotate-2">
            <Sparkles className="text-[#00d09c] mb-3" size={24} />
            <h4 className="font-bold text-sm uppercase tracking-wider mb-2 font-sans">AI Powered</h4>
            <p className="text-xs text-slate-500 font-sans leading-snug">Powered by Llama 3.3 Large Language Models for deepest sentiment extraction.</p>
          </div>
        </div>

        {/* Interaction Zone */}
        <section className="bg-[#1a1a1a] text-white p-10 rounded-sm mb-12 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
            <BookOpen size={120} />
          </div>
          
          <h3 className="font-['Playfair_Display'] text-3xl mb-8">Ready to brief your team?</h3>
          
          <div className="space-y-6 max-w-md font-sans">
            <div className="space-y-2">
              <label className="text-[10px] uppercase font-bold tracking-widest text-slate-400">Recipient Identification</label>
              <input 
                type="text" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Stakeholder Name"
                className="w-full bg-slate-800/50 border-b border-white/20 py-3 px-1 focus:outline-none focus:border-[#00d09c] transition-all text-lg"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] uppercase font-bold tracking-widest text-slate-400">Electronic Mailbox</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@example.com"
                className="w-full bg-slate-800/50 border-b border-white/20 py-3 px-1 focus:outline-none focus:border-[#00d09c] transition-all text-lg"
              />
            </div>

            <button 
              onClick={runAnalysis}
              disabled={loading}
              className={`w-full py-5 font-bold uppercase tracking-widest text-sm flex items-center justify-center gap-3 transition-all ${
                loading 
                  ? "bg-slate-700 text-slate-500" 
                  : "bg-white text-[#1a1a1a] hover:bg-[#00d09c] hover:text-white"
              }`}
            >
              {loading ? <Loader2 className="animate-spin" /> : <Send size={16} />}
              {loading ? "Analyzing..." : "Dispatch Pulse Report"}
            </button>

            <div className="h-4">
              {status && (
                <p className={`text-[10px] font-bold uppercase tracking-widest text-center ${complete ? "text-[#00d09c]" : "text-slate-500"}`}>
                  {status}
                </p>
              )}
            </div>
          </div>
        </section>

        {/* Feature Highlights */}
        <div className="grid grid-cols-3 gap-6 font-sans text-center">
            <div className="space-y-2">
                <Target size={20} className="mx-auto text-slate-400" />
                <span className="block text-[10px] font-black uppercase tracking-tighter">Strategic Actions</span>
            </div>
            <div className="space-y-2">
                <Quote size={20} className="mx-auto text-slate-400" />
                <span className="block text-[10px] font-black uppercase tracking-tighter">Vocal Sentiment</span>
            </div>
            <div className="space-y-2">
                <CheckCircle size={20} className="mx-auto text-slate-400" />
                <span className="block text-[10px] font-black uppercase tracking-tighter">Clean Filters</span>
            </div>
        </div>

        <footer className="mt-20 pt-8 border-t border-slate-100 text-[10px] text-slate-400 font-sans flex justify-between uppercase tracking-widest">
            <span>© 2026 Groww Intelligence Bureau</span>
            <span>Restricted Access Only</span>
        </footer>
      </div>
    </div>
  );
}
