/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Terminal, BookOpen, Cpu, ShieldCheck, CheckCircle2, Copy, FileText, ArrowRight, Layers } from 'lucide-react';

export default function App() {
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(id);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  const workflowSteps = [
    { title: "Research Planner", desc: "Formalizes research objective, constraints, and academic search queries", icon: BookOpen },
    { title: "Academic Retrieval", desc: "Live queries against arXiv API with Atom XML parsing & deduplication", icon: Layers },
    { title: "Paper Analyzer", desc: "Scientific extraction: problems, methodologies, datasets, findings, limits", icon: Cpu },
    { title: "Literature Review", desc: "Cross-paper comparative synthesis citing verified paper IDs [P001, P002...]", icon: FileText },
    { title: "Gap & Hypothesis", desc: "Detects provisional research gaps and formulates testable hypotheses", icon: ArrowRight },
    { title: "Experiment Designer", desc: "Protocol design, baselines, data leakage prevention, predictions", icon: Terminal },
    { title: "Research Judge", desc: "Deterministic citation checks & Gemini peer-review audit with revision loop", icon: ShieldCheck },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono flex flex-col items-center p-6 md:p-12">
      <div className="max-w-4xl w-full space-y-8">
        
        {/* Terminal Header */}
        <div className="border border-slate-800 rounded-lg bg-slate-900/80 shadow-2xl overflow-hidden backdrop-blur">
          <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
              <span className="text-xs text-slate-400 ml-2 font-semibold">autonomous-ai-researcher ~ terminal-app</span>
            </div>
            <span className="text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded">
              Python 3.10+ / LangGraph / Gemini
            </span>
          </div>

          <div className="p-6 md:p-8 space-y-6">
            <div className="space-y-2">
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                <Terminal className="w-8 h-8 text-cyan-400" />
                Autonomous AI Researcher
              </h1>
              <p className="text-slate-400 text-sm">
                Project: Autonomous AI Research & Data Science System | Module: AI Researcher Division
              </p>
            </div>

            {/* Terminal Instructions */}
            <div className="bg-black/60 rounded border border-slate-800 p-4 space-y-3">
              <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Run Directly in Terminal (VS Code / PyCharm):</p>
              
              <div className="space-y-2 text-xs md:text-sm">
                <div className="flex items-center justify-between bg-slate-900/90 p-2.5 rounded border border-slate-800">
                  <code className="text-cyan-300">python -m venv .venv && .venv\Scripts\Activate.ps1</code>
                  <button
                    onClick={() => copyToClipboard("python -m venv .venv && .venv\\Scripts\\Activate.ps1", "venv")}
                    className="text-slate-400 hover:text-white p-1"
                    title="Copy command"
                  >
                    {copiedCmd === "venv" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>

                <div className="flex items-center justify-between bg-slate-900/90 p-2.5 rounded border border-slate-800">
                  <code className="text-cyan-300">python -m pip install -r requirements.txt</code>
                  <button
                    onClick={() => copyToClipboard("python -m pip install -r requirements.txt", "pip")}
                    className="text-slate-400 hover:text-white p-1"
                    title="Copy command"
                  >
                    {copiedCmd === "pip" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>

                <div className="flex items-center justify-between bg-slate-900/90 p-2.5 rounded border border-slate-800">
                  <code className="text-emerald-400 font-bold">python main.py</code>
                  <button
                    onClick={() => copyToClipboard("python main.py", "run")}
                    className="text-slate-400 hover:text-white p-1"
                    title="Copy command"
                  >
                    {copiedCmd === "run" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>

                <div className="flex items-center justify-between bg-slate-900/90 p-2.5 rounded border border-slate-800">
                  <code className="text-yellow-300">python -m pytest AI_Researcher/tests -v</code>
                  <button
                    onClick={() => copyToClipboard("python -m pytest AI_Researcher/tests -v", "test")}
                    className="text-slate-400 hover:text-white p-1"
                    title="Copy command"
                  >
                    {copiedCmd === "test" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Test Results Badge */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-slate-900/60 border border-emerald-900/40 p-3.5 rounded flex items-center space-x-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                <div>
                  <div className="text-xs font-semibold text-emerald-400">25 / 25 Tests Passing</div>
                  <div className="text-[11px] text-slate-400">100% Offline Mocked Suite</div>
                </div>
              </div>
              <div className="bg-slate-900/60 border border-cyan-900/40 p-3.5 rounded flex items-center space-x-3">
                <Cpu className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                <div>
                  <div className="text-xs font-semibold text-cyan-400">Google GenAI Python SDK</div>
                  <div className="text-[11px] text-slate-400">gemini-3-flash-preview active</div>
                </div>
              </div>
              <div className="bg-slate-900/60 border border-purple-900/40 p-3.5 rounded flex items-center space-x-3">
                <Layers className="w-5 h-5 text-purple-400 flex-shrink-0" />
                <div>
                  <div className="text-xs font-semibold text-purple-400">LangGraph Orchestrator</div>
                  <div className="text-[11px] text-slate-400">Typed StateGraph & Branching</div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Workflow Diagram */}
        <div className="border border-slate-800 rounded-lg bg-slate-900/50 p-6 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Autonomous Multi-Agent Pipeline Architecture
          </h2>
          <div className="grid grid-cols-1 gap-2.5">
            {workflowSteps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={idx} className="flex items-start gap-3 p-3 bg-black/40 rounded border border-slate-800/80">
                  <div className="bg-slate-800/80 p-1.5 rounded text-cyan-400 flex-shrink-0 mt-0.5">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="space-y-0.5 text-xs">
                    <span className="font-bold text-slate-200">Stage {idx + 1}: {step.title}</span>
                    <p className="text-slate-400 text-[11px]">{step.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-slate-500 space-y-1">
          <p>Academic Research Automation • Autonomous AI Research & Data Science System</p>
          <p className="text-[11px] text-slate-600">All reports saved locally to AI_Researcher/reports/ in both Markdown and JSON.</p>
        </div>

      </div>
    </div>
  );
}
