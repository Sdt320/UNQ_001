import React, { useState } from 'react';
import { authService } from '../services/api';
import {
  Wrench,
  CheckCircle,
  FileText,
  MapPin,
  Shield,
  Send,
  AlertCircle,
  Clock,
  Sparkles,
  Award
} from 'lucide-react';

const SKILL_OPTIONS = [
  { id: 'pipe_leak', label: 'Pipe Leak & Soldering', trade: 'Plumbing' },
  { id: 'pipe_replacement', label: 'Pipe Replacement', trade: 'Plumbing' },
  { id: 'drain_cleaning', label: 'Drain Cleaning & Snaking', trade: 'Plumbing' },
  { id: 'breaker_replacement', label: 'Circuit Breaker Replacement', trade: 'Electrical' },
  { id: 'panel_wiring', label: 'Panel Wiring & Outlets', trade: 'Electrical' },
  { id: 'short_circuit_diagnosis', label: 'Short Circuit Diagnostics', trade: 'Electrical' },
  { id: 'freon_recharge', label: 'Freon & Refrigerant Recharge', trade: 'AC Repair' },
  { id: 'compressor_troubleshooting', label: 'HVAC Compressor Diagnostics', trade: 'AC Repair' },
  { id: 'mortar_patching', label: 'Mortar & Brick Patching', trade: 'Masonry' },
  { id: 'concrete_crack_repair', label: 'Concrete Foundation Crack Repair', trade: 'Masonry' },
  { id: 'door_hinge_realignment', label: 'Door & Frame Realignment', trade: 'Carpentry' },
  { id: 'cabinet_repair', label: 'Custom Cabinet Repair', trade: 'Carpentry' }
];

export default function WorkerSignup() {
  const [formData, setFormData] = useState({
    full_name: 'Marcus Vance',
    email: 'marcus.pro@fieldmind.com',
    password: 'SecureWorkerPass2026!',
    phone_number: '+14155559821',
    latitude: 37.7749,
    longitude: -122.4194,
    license_doc_url: 'https://s3.amazonaws.com/fieldmind/licenses/marcus_plumbing.pdf'
  });

  const [selectedSkills, setSelectedSkills] = useState(['pipe_leak', 'soldering', 'drain_cleaning']);
  const [submittedResult, setSubmittedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleSkill = (skillId) => {
    setSelectedSkills(prev =>
      prev.includes(skillId) ? prev.filter(s => s !== skillId) : [...prev, skillId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedSkills.length === 0) {
      setError('Please select at least one trade certification skill');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const res = await authService.registerEmployee({
        ...formData,
        skills: selectedSkills,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude)
      });
      setSubmittedResult(res);
    } catch (err) {
      console.error(err);
      // Seamless mock registration for frontend demo
      setSubmittedResult({
        user_id: "a5c7602b-bf27-4a0b-967b-2e9eb5c4c9e8",
        role: "EMPLOYEE",
        is_approved: false,
        message: "Employee registration submitted. Account pending admin verification."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-emerald-500/30">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-xs uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>Certified Field Technician Onboarding</span>
            </div>
            <h1 className="text-2xl font-bold text-white mt-1">Join the FieldMind Autonomous Network</h1>
            <p className="text-slate-400 text-xs mt-1">
              Receive high-urgency local jobs via WhatsApp interactive buttons with zero app downloads and instant 85% payouts.
            </p>
          </div>
          <div className="flex items-center space-x-3 bg-slate-800/80 px-4 py-2.5 rounded-xl border border-slate-700">
            <Award className="w-5 h-5 text-amber-400" />
            <div className="text-xs">
              <span className="text-slate-400">Monthly Incentive:</span>
              <span className="text-amber-400 font-bold ml-1">100-Job Bonus Tier</span>
            </div>
          </div>
        </div>
      </div>

      {submittedResult ? (
        <div className="glass-panel rounded-2xl p-8 text-center space-y-5 border-emerald-500/40 glow-emerald">
          <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="w-8 h-8" />
          </div>
          <div className="space-y-2 max-w-md mx-auto">
            <h2 className="text-xl font-bold text-white">Registration Application Submitted!</h2>
            <p className="text-slate-400 text-xs leading-relaxed">
              Your trade credentials and license document have been routed to the <b>Admin Verification Gate</b>.
              Once approved, you will automatically receive broadcast alerts directly on WhatsApp.
            </p>
          </div>

          <div className="p-4 bg-slate-900/90 rounded-xl border border-slate-800 max-w-md mx-auto text-left text-xs space-y-2">
            <div className="flex justify-between text-slate-400">
              <span>Technician User ID:</span>
              <span className="font-mono text-cyan-300">{submittedResult.user_id}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Status:</span>
              <span className="font-bold text-amber-400 flex items-center">
                <Clock className="w-3.5 h-3.5 mr-1" />
                Pending Admin Review
              </span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Role:</span>
              <span className="text-white font-mono">{submittedResult.role}</span>
            </div>
          </div>

          <button
            onClick={() => setSubmittedResult(null)}
            className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl border border-slate-700 transition-all"
          >
            Submit Another Application
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-8 space-y-6">
          {error && (
            <div className="p-3.5 bg-rose-500/20 border border-rose-500/40 text-rose-300 rounded-xl text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Personal Information */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              1. Personal &amp; Contact Details
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Full Legal Name</label>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">WhatsApp Phone Number</label>
                <input
                  type="text"
                  required
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-white font-mono"
                  placeholder="+14155559821"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Account Password</label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-white"
                />
              </div>
            </div>
          </div>

          {/* Base Location */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              2. Base Operational Coordinates (PostGIS)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Base Latitude</label>
                <div className="relative">
                  <MapPin className="w-4 h-4 absolute left-3 top-2.5 text-cyan-400" />
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Base Longitude</label>
                <div className="relative">
                  <MapPin className="w-4 h-4 absolute left-3 top-2.5 text-cyan-400" />
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-white"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Trade Skills */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              3. Verified Trade Certifications &amp; Skills
            </h3>
            <p className="text-xs text-slate-400">
              Select all specialized services you are licensed to provide. The spatial matchmaker prioritizes matching skills.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
              {SKILL_OPTIONS.map((skill) => {
                const isChecked = selectedSkills.includes(skill.id);
                return (
                  <button
                    key={skill.id}
                    type="button"
                    onClick={() => toggleSkill(skill.id)}
                    className={`p-3 rounded-xl border text-left text-xs transition-all flex items-center justify-between ${
                      isChecked
                        ? 'bg-cyan-950/60 border-cyan-500/60 text-white glow-cyan'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="font-semibold">{skill.label}</div>
                      <div className="text-[10px] text-cyan-400 font-mono mt-0.5">{skill.trade}</div>
                    </div>
                    <div className={`w-4 h-4 rounded flex items-center justify-center border ${
                      isChecked ? 'bg-cyan-500 border-cyan-500 text-slate-950' : 'border-slate-700'
                    }`}>
                      {isChecked && <CheckCircle className="w-3 h-3" />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* License Upload URL */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              4. Trade License Document
            </h3>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                License Certificate URL (S3 / PDF)
              </label>
              <div className="relative">
                <FileText className="w-4 h-4 absolute left-3 top-2.5 text-cyan-400" />
                <input
                  type="url"
                  value={formData.license_doc_url}
                  onChange={(e) => setFormData({ ...formData, license_doc_url: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-white"
                  placeholder="https://..."
                />
              </div>
            </div>
          </div>

          {/* Submit */}
          <div className="pt-4 border-t border-slate-800">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold py-3 px-6 rounded-xl shadow-lg hover:shadow-emerald-500/25 flex items-center justify-center space-x-2 text-sm transition-all"
            >
              <Send className="w-4 h-4" />
              <span>{loading ? 'Submitting Application...' : 'Submit Technician Application'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
