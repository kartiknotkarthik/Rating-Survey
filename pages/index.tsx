import React, { useState } from 'react';
import Head from 'next/head';
import { Mail, Zap, CheckCircle, Loader2, BarChart3, ShieldCheck } from 'lucide-react';

export default function GrowwPulseDashboard() {
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
    setStatus("Fetching reviews from Play Store...");
    
    try {
      const response = await fetch('/api/pulse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setStatus("Analysis complete. Email sent!");
        setComplete(true);
      } else {
        setStatus(`Error: ${result.message || 'Unknown error'}`);
      }
    } catch (err) {
      setStatus("Failed to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8 font-sans">
      <Head>
        <title>GROWW Pulse | Review Analyzer</title>
      </Head>
      
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-12">
          <div className="bg-[#00d09c] p-3 rounded-2xl shadow-lg shadow-[#00d09c]/20">
            <BarChart3 size={32} className="text-[#0f172a]" />
          </div>
          <div>
            <h1 className="text-4xl font-bold tracking-tight">GROWW <span className="text-[#00d09c]">Pulse</span></h1>
            <p className="text-slate-400">Automated Weekly Review Analyzer</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl backdrop-blur-xl transition-all hover:border-[#00d09c]/30">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Zap size={20} className="text-[#00d09c]" /> Configuration
            </h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Stakeholder Name</label>
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Karry"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#00d09c]/50 transition-all text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Delivery Email</label>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. kartik@gmail.com"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#00d09c]/50 transition-all text-white"
                />
              </div>

              <button 
                onClick={runAnalysis}
                disabled={loading}
                className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg ${
                  loading 
                    ? "bg-slate-800 text-slate-500 cursor-not-allowed" 
                    : "bg-[#00d09c] text-[#0f172a] hover:bg-[#00b08a] hover:scale-[1.02]"
                }`}
              >
                {loading ? <Loader2 className="animate-spin" /> : <Mail size={18} />}
                {loading ? "Processing..." : "Generate & Send Pulse"}
              </button>
            </div>
          </div>

          <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl backdrop-blur-xl flex flex-col justify-center items-center text-center">
            {!loading && !complete && (
              <div>
                <ShieldCheck size={64} className="text-slate-800 mb-4 mx-auto" />
                <h3 className="text-xl font-medium text-slate-500">Ready to Analyze</h3>
                <p className="text-slate-600 mt-2 text-sm">Fill in the details to start the pipeline</p>
              </div>
            )}

            {loading && (
              <div>
                <Loader2 size={48} className="text-[#00d09c] animate-spin mb-4 mx-auto" />
                <p className="text-[#00d09c] font-medium">{status}</p>
              </div>
            )}

            {complete && (
              <div>
                <CheckCircle size={64} className="text-[#00d09c] mb-4 mx-auto" />
                <h3 className="text-2xl font-bold">Pulse Sent!</h3>
                <p className="text-slate-400 mt-2">The report has been delivered to <strong>{email}</strong></p>
                <button 
                  onClick={() => setComplete(false)}
                  className="mt-6 text-sm text-slate-500 hover:text-white transition-colors"
                >
                  Create another report
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
