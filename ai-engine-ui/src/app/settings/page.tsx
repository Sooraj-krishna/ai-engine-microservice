'use client';

import { API_BASE_URL, WS_BASE_URL } from '@/lib/config';

import { useState, useEffect } from "react";

export default function SettingsPage() {
  const [useAiClassification, setUseAiClassification] = useState(false);
  const [useImprovedFixer, setUseImprovedFixer] = useState(false);
  const [testFixesBeforeApply, setTestFixesBeforeApply] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [message, setMessage] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || API_BASE_URL;

  // Load current setting
  useEffect(() => {
    fetchSetting();
  }, []);

  const fetchSetting = async () => {
    try {
      // Fetch AI classification setting
      const aiResponse = await fetch(`${API_URL}/settings/ai-classification`);
      const aiData = await aiResponse.json();
      setUseAiClassification(aiData.use_ai_classification);

      // Fetch config for other settings
      const configResponse = await fetch(`${API_URL}/config`);
      const configData = await configResponse.json();
      setUseImprovedFixer(configData.use_improved_fixer || false);
      setTestFixesBeforeApply(configData.test_fixes_before_apply !== undefined ? configData.test_fixes_before_apply : true);
      
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch settings:", error);
      setLoading(false);
    }
  };

  const handleToggle = async (enabled: boolean) => {
    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/settings/ai-classification`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          use_ai_classification: enabled,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setUseAiClassification(enabled);
        setMessage(data.message);
        setTimeout(() => setMessage(""), 5000);
      } else {
        setMessage("Failed to update setting");
      }
    } catch (error) {
      console.error("Failed to update setting:", error);
      setMessage("Error updating setting");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] text-white flex items-center justify-center">
        <div className="text-cyan-400">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="bg-black min-h-screen pt-28 pb-24 px-4 relative overflow-hidden">
      {/* Background ambient glows */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-[150px] -ml-60 -mt-60 pointer-events-none" />

      <div className="max-w-4xl mx-auto relative z-10">
        {/* ── PAGE HEADER ─────────────────────────────── */}
        <div className="mb-16">
          <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 mb-3">
            AI Engine · Configuration
          </p>
          <h1 className="text-5xl md:text-6xl font-bold uppercase tracking-tighter text-white leading-none mb-4">
            System <span className="text-zinc-500 italic">Settings</span>
          </h1>
          <p className="text-base text-zinc-500 font-light max-w-xl">
            Configure autonomous heuristics · Adjust AI intensity · Manage integration tokens
          </p>
        </div>

        {/* Success Message */}
        {message && (
          <div className="mb-8 p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-[10px] font-black uppercase tracking-widest text-center animate-in fade-in zoom-in duration-300">
            {message}
          </div>
        )}

        {/* General Settings */}
        <div className="premium-card p-8 mb-6">
          <div className="flex items-center gap-4 mb-8 pb-4 border-b border-white/5">
            <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center">
              <span className="text-xs">⚙️</span>
            </div>
            <h2 className="text-xs font-black uppercase tracking-[0.3em] text-white">General Configuration</h2>
          </div>
          <p className="text-zinc-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed mb-6">
            Basic configuration options for the AI Engine intelligence core.
          </p>
          <div className="p-6 bg-white/[0.02] border border-white/5 rounded-2xl border-dashed">
            <p className="text-[10px] text-zinc-700 font-black uppercase tracking-widest text-center">Modules initializing...</p>
          </div>
        </div>

        {/* Advanced Options */}
        <div className="premium-card overflow-hidden">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full p-8 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center gap-4 text-left">
              <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center">
                <span className="text-xs">⚡</span>
              </div>
              <div>
                <h2 className="text-xs font-black uppercase tracking-[0.3em] text-white">Advanced Heuristics</h2>
                <p className="text-[10px] text-zinc-600 font-bold uppercase tracking-widest mt-1">Performance & API Tuning</p>
              </div>
            </div>
            <svg
              className={`w-4 h-4 text-zinc-500 transition-transform duration-500 ${showAdvanced ? "rotate-180" : ""}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <div className={`transition-all duration-500 ease-in-out ${showAdvanced ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"} overflow-hidden`}>
            <div className="p-8 border-t border-white/5 space-y-12">
              
              {/* AI Classification */}
              <div className="space-y-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center">🧠</div>
                      <div>
                        <h3 className="text-sm font-black uppercase tracking-tight text-white">AI-Powered Bug Classification</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`w-1.5 h-1.5 rounded-full ${useAiClassification ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-zinc-700"}`} />
                          <span className="text-[9px] font-black uppercase tracking-widest text-zinc-500">{useAiClassification ? "Active" : "Inactive"}</span>
                        </div>
                      </div>
                    </div>
                    <p className="text-zinc-500 text-xs leading-relaxed max-w-xl">
                      Intelligently classify bug severity using Gemini AI. Provides high accuracy context-aware analysis of discovered anomalies.
                    </p>
                  </div>
                  <button
                    onClick={() => handleToggle(!useAiClassification)}
                    disabled={saving}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all ${useAiClassification ? "bg-white" : "bg-zinc-800"}`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full transition-transform ${useAiClassification ? "translate-x-6 bg-black" : "translate-x-1 bg-zinc-600"}`} />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                    <div className="text-[9px] font-black uppercase tracking-widest text-white mb-3 flex items-center gap-2">
                      <span className="w-1 h-1 bg-white rounded-full" /> AI Engine
                    </div>
                    <ul className="space-y-2 text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
                      <li className="flex items-center gap-2">✓ ~95% Accuracy</li>
                      <li className="flex items-center gap-2">✓ Context Aware</li>
                    </ul>
                  </div>
                  <div className="p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                    <div className="text-[9px] font-black uppercase tracking-widest text-zinc-600 mb-3 flex items-center gap-2">
                      <span className="w-1 h-1 bg-zinc-600 rounded-full" /> Rule-Based
                    </div>
                    <ul className="space-y-2 text-[10px] text-zinc-700 font-bold uppercase tracking-widest">
                      <li className="flex items-center gap-2">✓ 100+ Patterns</li>
                      <li className="flex items-center gap-2">✓ Zero Token Cost</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Improved Fixer */}
              <div className="space-y-6 pt-12 border-t border-white/5">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center">🔧</div>
                      <div>
                        <h3 className="text-sm font-black uppercase tracking-tight text-white">Enhanced Fixer Core</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`w-1.5 h-1.5 rounded-full ${useImprovedFixer ? "bg-emerald-500" : "bg-zinc-700"}`} />
                          <span className="text-[9px] font-black uppercase tracking-widest text-zinc-500">{useImprovedFixer ? "Active" : "Inactive"}</span>
                        </div>
                      </div>
                    </div>
                    <p className="text-zinc-500 text-xs leading-relaxed max-w-xl">
                      Advanced resolution heuristics with code diffing, semantic chunking, and incremental patch application.
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      const enabled = !useImprovedFixer;
                      setUseImprovedFixer(enabled);
                      try {
                        await fetch(`${API_URL}/configure`, {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ useImprovedFixer: enabled }),
                        });
                        setMessage("Settings Synchronized");
                        setTimeout(() => setMessage(""), 3000);
                      } catch (error) {
                        setUseImprovedFixer(!enabled);
                      }
                    }}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all ${useImprovedFixer ? "bg-white" : "bg-zinc-800"}`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full transition-transform ${useImprovedFixer ? "translate-x-6 bg-black" : "translate-x-1 bg-zinc-600"}`} />
                  </button>
                </div>
              </div>

              {/* Testing Mode */}
              <div className="space-y-6 pt-12 border-t border-white/5">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center">🧪</div>
                      <div>
                        <h3 className="text-sm font-black uppercase tracking-tight text-white">Isolation Validation</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`w-1.5 h-1.5 rounded-full ${testFixesBeforeApply ? "bg-emerald-500" : "bg-zinc-700"}`} />
                          <span className="text-[9px] font-black uppercase tracking-widest text-zinc-500">{testFixesBeforeApply ? "Mandatory" : "Optional"}</span>
                        </div>
                      </div>
                    </div>
                    <p className="text-zinc-500 text-xs leading-relaxed max-w-xl">
                      Validate resolutions in isolated environments before deployment. Ensures zero regression policy for all automated patches.
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      const enabled = !testFixesBeforeApply;
                      setTestFixesBeforeApply(enabled);
                      try {
                        await fetch(`${API_URL}/configure`, {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ testFixesBeforeApply: enabled }),
                        });
                        setMessage("Settings Synchronized");
                        setTimeout(() => setMessage(""), 3000);
                      } catch (error) {
                        setTestFixesBeforeApply(!enabled);
                      }
                    }}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all ${testFixesBeforeApply ? "bg-white" : "bg-zinc-800"}`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full transition-transform ${testFixesBeforeApply ? "translate-x-6 bg-black" : "translate-x-1 bg-zinc-600"}`} />
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
