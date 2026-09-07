import React, { useState } from 'react';
import { requestService, webhookService } from '../services/api';
import {
  Mic,
  Send,
  MapPin,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileText,
  DollarSign,
  ShieldCheck,
  Zap,
  Sparkles,
  RefreshCw,
  PhoneCall,
  Download
} from 'lucide-react';

const PRESET_ISSUES = [
  {
    label: "🚨 Burst Pipe Emergency",
    category: "Plumbing",
    prompt: "Emergency: My bathroom pipe burst under the sink and clean water is flooding everywhere. Need immediate shutoff and pipe replacement."
  },
  {
    label: "⚡ Sparking Circuit Breaker",
    category: "Electrical",
    prompt: "The main breaker is sparking loudly with burning smell and panel switches keep tripping whenever AC starts."
  },
  {
    label: "❄️ AC Blowing Warm Air",
    category: "AC Repair",
    prompt: "Central AC unit is blowing hot air and condenser unit is making buzzing noise. May need freon recharge."
  },
  {
    label: "🧱 Exterior Brick Cracks",
    category: "Masonry",
    prompt: "Severe foundation crack on exterior brick wall requiring structural mortar patching before heavy rain."
  },
  {
    label: "🚪 Broken Kitchen Cabinet",
    category: "Carpentry",
    prompt: "Custom oak cabinet door broke off its hinge and timber frame is misaligned."
  }
];

export default function CustomerPortal() {
  const [promptText, setPromptText] = useState(PRESET_ISSUES[0].prompt);
  const [latitude, setLatitude] = useState(37.7793);
  const [longitude, setLongitude] = useState(-122.4230);
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [jobResponse, setJobResponse] = useState(null);
  const [claimedOfficer, setClaimedOfficer] = useState(null);
  const [stepStatus, setStepStatus] = useState('IDLE'); // IDLE, DISPATCHED, CLAIMED, SETTLED

  const handleSubmitRequest = async (e) => {
    e?.preventDefault();
    if (!promptText.trim()) return;

    setLoading(true);
    setClaimedOfficer(null);
    try {
      const res = await requestService.createRequest({
        user_prompt: promptText,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        audio_url: isRecording ? "https://fieldmind.storage/audio/voice_intake_01.ogg" : null
      });
      setJobResponse(res);
      setStepStatus('DISPATCHED');
    } catch (err) {
      console.error(err);
      // Fallback state for seamless frontend demo
      setJobResponse({
        job_id: "f29b439c-85e7-4b77-a89e-4e432a514d31",
        status: "DISPATCHED",
        extracted_intent: {
          category: "Plumbing",
          required_skills: ["pipe_leak", "pipe_replacement"],
          urgency: "HIGH",
          estimated_scope: "Pipe joint replacement, water shutoff, clamp tools"
        },
        search_radius_meters: 10000,
        candidates_notified: 3
      });
      setStepStatus('DISPATCHED');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateTechnicianAccept = async () => {
    if (!jobResponse) return;
    setLoading(true);
    try {
      const claimRes = await requestService.claimJob(
        jobResponse.job_id,
        "officer-001",
        "Marcus Vance",
        "+14155559821"
      );
      setClaimedOfficer({
        name: "Marcus Vance",
        phone: "+14155559821",
        rating: 4.92,
        eta: "8-12 mins",
        skills: ["pipe_leak", "soldering"]
      });
      setStepStatus('SETTLED');
    } catch (err) {
      console.error(err);
      // Optimistic demo completion
      setClaimedOfficer({
        name: "Marcus Vance",
        phone: "+14155559821",
        rating: 4.92,
        eta: "8-12 mins",
        skills: ["pipe_leak", "soldering"]
      });
      setStepStatus('SETTLED');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateVoice = () => {
    setIsRecording(true);
    setPromptText("🎙️ [Audio Ingesting: 0:08s] Emergency: Master bathroom pipe burst behind valve, clean water flooding room!");
    setTimeout(() => {
      setIsRecording(false);
      setPromptText("Emergency: Master bathroom pipe burst behind valve, clean water flooding room! Need high-urgency plumber.");
    }, 2000);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-cyan-500/30">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-xs uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>Multimodal Autonomous Intake</span>
            </div>
            <h1 className="text-2xl font-bold text-white mt-1">Instant Home Service Request</h1>
            <p className="text-slate-400 text-xs mt-1">
              Voice notes or text queries are diagnosed via Whisper &amp; GPT-4o-mini and matched via PostGIS 10km radius.
            </p>
          </div>
          <div className="flex items-center space-x-3 bg-slate-800/80 px-4 py-2.5 rounded-xl border border-slate-700">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <div className="text-xs">
              <span className="text-slate-400">Escrow Security:</span>
              <span className="text-white font-bold ml-1">Stripe 85/15 Hold</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form (Col span 5) */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 space-y-6">
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <span>Describe Your Repair</span>
          </h2>

          {/* Quick Presets */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Quick Diagnostic Scenarios
            </label>
            <div className="flex flex-wrap gap-1.5">
              {PRESET_ISSUES.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPromptText(preset.prompt)}
                  className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-cyan-900/40 hover:text-cyan-300 border border-slate-700 text-slate-300 transition-all text-left"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmitRequest} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Problem Description or Voice Note
              </label>
              <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                rows={4}
                required
                className="w-full bg-slate-900/90 border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 leading-relaxed font-sans transition-all"
                placeholder="E.g., My kitchen sink is overflowing with water..."
              />
            </div>

            {/* Coordinates / Map Pin */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Latitude (WGS84)
                </label>
                <div className="relative">
                  <MapPin className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-cyan-400" />
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-2 py-1.5 text-xs text-white"
                  />
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Longitude (WGS84)
                </label>
                <div className="relative">
                  <MapPin className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-cyan-400" />
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-2 py-1.5 text-xs text-white"
                  />
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={handleSimulateVoice}
                className={`px-4 py-2.5 rounded-xl border flex items-center justify-center space-x-2 text-xs font-semibold transition-all ${
                  isRecording
                    ? 'bg-rose-500/20 border-rose-500 text-rose-300 animate-pulse'
                    : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200'
                }`}
              >
                <Mic className={`w-4 h-4 ${isRecording ? 'text-rose-400' : 'text-cyan-400'}`} />
                <span>{isRecording ? 'Listening...' : 'Voice Note'}</span>
              </button>

              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-2.5 px-4 rounded-xl shadow-lg hover:shadow-cyan-500/25 flex items-center justify-center space-x-2 text-xs transition-all"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Dispatch Multi-Agent</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Right Status & Lifecycle Tracker (Col span 7) */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Clock className="w-5 h-5 text-cyan-400" />
              <span>Live Booking Lifecycle</span>
            </h2>
            {jobResponse && (
              <span className="text-[11px] font-mono text-cyan-300 bg-cyan-950/60 px-2.5 py-1 rounded-full border border-cyan-800">
                Job #{jobResponse.job_id?.slice(0, 8)}...
              </span>
            )}
          </div>

          {!jobResponse ? (
            <div className="text-center py-16 text-slate-500 space-y-3">
              <Zap className="w-12 h-12 mx-auto text-cyan-500/30 animate-pulse-slow" />
              <p className="font-semibold text-slate-400 text-sm">Awaiting Repair Submission</p>
              <p className="text-xs max-w-sm mx-auto">
                Submit an issue using voice note or text on the left to trigger the LangGraph diagnostic engine.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Intent Diagnostic Badge */}
              <div className="p-4 bg-slate-900/90 rounded-xl border border-cyan-500/30 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-400 uppercase font-semibold">Diagnosed Trade:</span>
                    <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-bold text-xs border border-cyan-500/40">
                      {jobResponse.extracted_intent?.category}
                    </span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                    jobResponse.extracted_intent?.urgency === 'EMERGENCY'
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  }`}>
                    {jobResponse.extracted_intent?.urgency} URGENCY
                  </span>
                </div>

                <div className="text-xs text-slate-300">
                  <span className="text-slate-400">Estimated Scope: </span>
                  {jobResponse.extracted_intent?.estimated_scope}
                </div>

                <div className="flex flex-wrap gap-1 items-center">
                  <span className="text-[11px] text-slate-400 mr-1">Required Skills:</span>
                  {jobResponse.extracted_intent?.required_skills?.map((s, idx) => (
                    <span key={idx} className="text-[10px] bg-slate-800 text-slate-200 px-2 py-0.5 rounded border border-slate-700">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Step Progress Visualizer */}
              <div className="space-y-4">
                {/* Step 1: PostGIS Match */}
                <div className="flex items-start space-x-3 text-xs">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">PostGIS Spatial Matchmaking Completed</div>
                    <div className="text-slate-400 mt-0.5">
                      Queried 10,000m radius using ST_DWithin. Filtered for approved technicians. Notified {jobResponse.candidates_notified} candidates via WhatsApp interactive templates.
                    </div>
                  </div>
                </div>

                {/* Step 2: WhatsApp Webhook & Redis Mutex Claim */}
                <div className="flex items-start space-x-3 text-xs">
                  {stepStatus === 'SETTLED' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <Clock className="w-5 h-5 text-amber-400 shrink-0 mt-0.5 animate-spin" />
                  )}
                  <div className="w-full space-y-2">
                    <div className="font-semibold text-white">
                      {stepStatus === 'SETTLED' ? 'Technician Claimed & Lock Won' : 'Awaiting Technician Response (Interactive WhatsApp Reply)'}
                    </div>

                    {stepStatus === 'DISPATCHED' && (
                      <div className="p-3 bg-slate-800/80 rounded-lg border border-slate-700 flex items-center justify-between">
                        <span className="text-slate-300 text-xs">
                          Simulate Marcus Vance clicking <span className="text-cyan-400 font-bold">[Accept Job]</span> on WhatsApp:
                        </span>
                        <button
                          type="button"
                          onClick={handleSimulateTechnicianAccept}
                          disabled={loading}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs transition-all shadow"
                        >
                          Accept via WhatsApp
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Step 3: Assigned Technician & Escrow Hold */}
                {claimedOfficer && (
                  <div className="p-4 bg-slate-900/90 rounded-xl border border-emerald-500/40 space-y-3 glow-emerald">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span className="font-bold text-white text-sm">{claimedOfficer.name}</span>
                        <span className="text-xs text-amber-400 font-semibold">★ {claimedOfficer.rating}</span>
                      </div>
                      <span className="text-xs text-emerald-400 font-mono">ETA: {claimedOfficer.eta}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-800 text-slate-300">
                      <div>
                        <span className="text-slate-400">Phone: </span>
                        <span className="font-mono text-cyan-300">{claimedOfficer.phone}</span>
                      </div>
                      <div>
                        <span className="text-slate-400">Escrow Hold: </span>
                        <span className="font-semibold text-emerald-400">$120.00 Authorized</span>
                      </div>
                    </div>

                    {/* Invoice & Vision Completion Card */}
                    <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                      <div className="text-xs text-slate-400">
                        <span className="text-emerald-400 font-bold">Status:</span> Settled (85% tech: $102.00 / 15% platform: $18.00)
                      </div>
                      <button
                        onClick={() => alert(`Downloading Official Service Invoice PDF for Job #${jobResponse.job_id.slice(0, 8)}...`)}
                        className="inline-flex items-center space-x-1.5 px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg shadow transition-all"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>PDF Invoice</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
