"use client";

import { useState, useEffect } from "react";

export default function SettingsPage() {
  const [useAiClassification, setUseAiClassification] = useState(false);
  const [useImprovedFixer, setUseImprovedFixer] = useState(false);
  const [testFixesBeforeApply, setTestFixesBeforeApply] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [message, setMessage] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
    <div className="min-h-screen bg-[#0A0A0F] text-white">
      {/* Header */}
      <div className="border-b border-cyan-500/20 bg-gradient-to-r from-cyan-500/5 to-transparent">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Settings
            </h1>
          </div>
          <p className="text-gray-400">Configure AI Engine behavior and preferences</p>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Success Message */}
        {message && (
          <div className="mb-6 p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            {message}
          </div>
        )}

        {/* General Settings */}
        <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-cyan-500/20 rounded-xl p-6 shadow-xl mb-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <span>⚙️</span>
            General Settings
          </h2>
          <p className="text-gray-400 text-sm">
            Basic configuration options for the AI Engine.
          </p>
          <div className="mt-4 p-4 bg-gray-800/50 rounded-lg opacity-50">
            <p className="text-sm text-gray-400">Coming soon...</p>
          </div>
        </div>

        {/* Advanced Options - Collapsible */}
        <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-cyan-500/20 rounded-xl shadow-xl overflow-hidden">
          {/* Header - Clickable */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-cyan-500/5 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500/20 to-red-500/20 flex items-center justify-center">
                ⚡
              </div>
              <div className="text-left">
                <h2 className="text-xl font-semibold text-white">Advanced Options</h2>
                <p className="text-sm text-gray-400">Performance and API configuration</p>
              </div>
            </div>
            <svg
              className={`w-6 h-6 text-gray-400 transition-transform ${
                showAdvanced ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          {/* Collapsible Content */}
          <div
            className={`transition-all duration-300 ease-in-out ${
              showAdvanced ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
            } overflow-hidden`}
          >
            <div className="px-6 pb-6 pt-2 border-t border-cyan-500/10 max-h-[1200px] overflow-y-auto"
              style={{ scrollbarWidth: 'thin', scrollbarColor: '#06b6d4 #1f2937' }}
            >
              {/* AI Classification Setting */}
              <div className="mt-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                        🧠
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          AI-Powered Bug Classification
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className={`inline-block w-2 h-2 rounded-full ${
                              useAiClassification ? "bg-green-500" : "bg-gray-500"
                            }`}
                          ></span>
                          <span className="text-sm text-gray-400">
                            {useAiClassification ? "Enabled" : "Disabled"}
                          </span>
                        </div>
                      </div>
                    </div>

                    <p className="text-gray-400 text-sm mt-4 leading-relaxed">
                      When enabled, uses Gemini AI to intelligently classify bug severity
                      with high accuracy. When disabled, uses rule-based classification to
                      save API tokens.
                    </p>

                    {/* Comparison Table */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                      {/* AI Classification */}
                      <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
                        <div className="font-semibold text-purple-400 mb-2 flex items-center gap-2 text-sm">
                          <span>🤖</span>
                          <span>AI Classification</span>
                        </div>
                        <ul className="space-y-1.5 text-xs text-gray-300">
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>~95% accuracy</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Context-aware analysis</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-red-500">✗</span>
                            <span>Uses API tokens</span>
                          </li>
                        </ul>
                      </div>

                      {/* Rule-Based */}
                      <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3">
                        <div className="font-semibold text-cyan-400 mb-2 flex items-center gap-2 text-sm">
                          <span>📋</span>
                          <span>Rule-Based</span>
                        </div>
                        <ul className="space-y-1.5 text-xs text-gray-300">
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>~85-90% accuracy</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>100+ keyword patterns</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>No API token cost</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Toggle Switch */}
                  <div className="ml-6 flex-shrink-0">
                    <button
                      onClick={() => handleToggle(!useAiClassification)}
                      disabled={saving}
                      className={`relative inline-flex h-10 w-20 items-center rounded-full transition-colors ${
                        useAiClassification
                          ? "bg-gradient-to-r from-purple-500 to-pink-500"
                          : "bg-gray-700"
                      } ${saving ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                    >
                      <span
                        className={`inline-block h-8 w-8 transform rounded-full bg-white shadow-lg transition-transform ${
                          useAiClassification ? "translate-x-10" : "translate-x-1"
                        }`}
                      />
                    </button>
                    {saving && (
                      <div className="text-xs text-gray-400 mt-2 text-center">
                        Saving...
                      </div>
                    )}
                  </div>
                </div>

                {/* API Token Warning */}
                {useAiClassification && (
                  <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                    <div className="flex items-start gap-3">
                      <span className="text-xl">⚠️</span>
                      <div className="flex-1">
                        <p className="text-yellow-400 font-semibold mb-1 text-sm">
                          API Token Usage
                        </p>
                        <p className="text-xs text-gray-300">
                          AI classification uses Gemini API tokens for each bug detected.
                          Monitor your usage in the{" "}
                          <a
                            href="https://aistudio.google.com/apikey"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-cyan-400 hover:text-cyan-300 underline"
                          >
                            Google AI Studio
                          </a>
                          .
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Divider */}
              <div className="border-t border-cyan-500/10 my-6"></div>

              {/* Use Improved Fixer */}
              <div className="mt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-red-500/20 to-orange-500/20 flex items-center justify-center">
                        🔧
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          Use Improved Fixer
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className={`inline-block w-2 h-2 rounded-full ${
                              useImprovedFixer ? "bg-green-500" : "bg-gray-500"
                            }`}
                          ></span>
                          <span className="text-sm text-gray-400">
                            {useImprovedFixer ? "Enabled" : "Disabled"}
                          </span>
                        </div>
                      </div>
                    </div>

                    <p className="text-gray-400 text-sm mt-4 leading-relaxed">
                      Enable advanced fixing with code diffs, chunking, and incremental fixes. More accurate but experimental.
                    </p>

                    {/* Feature Cards */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                      {/* Standard Fixer */}
                      <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
                        <div className="font-semibold text-gray-400 mb-2 flex items-center gap-2 text-sm">
                          <span>📝</span>
                          <span>Standard Fixer</span>
                        </div>
                        <ul className="space-y-1.5 text-xs text-gray-300">
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Basic fixes</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Fast execution</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-yellow-500">~</span>
                            <span>Limited accuracy</span>
                          </li>
                        </ul>
                      </div>

                      {/* Improved Fixer */}
                      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                        <div className="font-semibold text-red-400 mb-2 flex items-center gap-2 text-sm">
                          <span>⚡</span>
                          <span>Improved Fixer</span>
                        </div>
                        <ul className="space-y-1.5 text-xs text-gray-300">
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Code diffs & chunking</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Incremental fixes</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Higher accuracy</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Toggle Switch */}
                  <div className="ml-6 flex-shrink-0">
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
                          setMessage("✅ Setting updated successfully!");
                          setTimeout(() => setMessage(""), 3000);
                        } catch (error) {
                          console.error("Failed to update:", error);
                          setMessage("❌ Failed to update setting");
                        }
                      }}
                      disabled={saving}
                      className={`relative inline-flex h-10 w-20 items-center rounded-full transition-colors ${
                        useImprovedFixer
                          ? "bg-gradient-to-r from-red-500 to-orange-500"
                          : "bg-gray-700"
                      } ${saving ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                    >
                      <span
                        className={`inline-block h-8 w-8 transform rounded-full bg-white shadow-lg transition-transform ${
                          useImprovedFixer ? "translate-x-10" : "translate-x-1"
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>

              {/* Divider */}
              <div className="border-t border-cyan-500/10 my-6"></div>

              {/* Test Fixes Before Applying */}
              <div className="mt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center">
                        🧪
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          Test Fixes Before Applying
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className={`inline-block w-2 h-2 rounded-full ${
                              testFixesBeforeApply ? "bg-green-500" : "bg-gray-500"
                            }`}
                          ></span>
                          <span className="text-sm text-gray-400">
                            {testFixesBeforeApply ? "Enabled" : "Disabled"}
                          </span>
                        </div>
                      </div>
                    </div>

                    <p className="text-gray-400 text-sm mt-4 leading-relaxed">
                      Test fixes in isolated environment before creating PRs. Prevents bad fixes from going live.
                      <span className="text-green-400 font-semibold"> Recommended: ON</span>
                    </p>

                    {/* Feature Cards */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                      {/* Without Testing */}
                      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                        <div className="font-semibold text-red-400 mb-2 flex items-center gap-2 text-sm">
                          <span>⚠️</span>
                          <span>Without Testing</span>
                        </div>
                        <ul className="space-y-1.5 text-xs text-gray-300">
                          <li className="flex items-start gap-2">
                            <span className="text-red-500">✗</span>
                            <span>Bad fixes may go live</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-red-500">✗</span>
                            <span>Risk of breaking code</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Faster deployment</span>
                          </li>
                        </ul>
                      </div>

                      {/* With Testing */}
                      <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                        <div className="font-semibold text-green-400 mb-2 flex items-center gap-2 text-sm">
                          <span>✅</span>
                          <span>With Testing</span>
                        </div>
                        <ul className="space-y-1.5 text-xs text-gray-300">
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Validated fixes only</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Safe deployments</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-green-500">✓</span>
                            <span>Production-ready</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Toggle Switch */}
                  <div className="ml-6 flex-shrink-0">
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
                          setMessage("✅ Setting updated successfully!");
                          setTimeout(() => setMessage(""), 3000);
                        } catch (error) {
                          console.error("Failed to update:", error);
                          setMessage("❌ Failed to update setting");
                        }
                      }}
                      disabled={saving}
                      className={`relative inline-flex h-10 w-20 items-center rounded-full transition-colors ${
                        testFixesBeforeApply
                          ? "bg-gradient-to-r from-green-500 to-emerald-500"
                          : "bg-gray-700"
                      } ${saving ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                    >
                      <span
                        className={`inline-block h-8 w-8 transform rounded-full bg-white shadow-lg transition-transform ${
                          testFixesBeforeApply ? "translate-x-10" : "translate-x-1"
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
