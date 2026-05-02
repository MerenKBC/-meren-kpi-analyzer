"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Modal } from "@/components/Modal";
import axios from "axios";
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  ShoppingCart, 
  Bell, 
  Search, 
  Sparkles, 
  Download 
} from "lucide-react";
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

const data = [
  { name: "Mon", revenue: 4000, orders: 24 },
  { name: "Tue", revenue: 3000, orders: 18 },
  { name: "Wed", revenue: 2000, orders: 12 },
  { name: "Thu", revenue: 2780, orders: 20 },
  { name: "Fri", revenue: 1890, orders: 15 },
  { name: "Sat", revenue: 2390, orders: 22 },
  { name: "Sun", revenue: 3490, orders: 30 },
];

export default function Dashboard() {
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [insight, setInsight] = useState<any>(null);
  const [activeMetric, setActiveMetric] = useState("");

  const handleExplain = async (metric: string) => {
    setActiveMetric(metric);
    setIsAiModalOpen(true);
    setAiLoading(true);
    setInsight(null);
    
    try {
      const response = await axios.post(`http://localhost:8000/ai/explain?metric_name=${metric.toLowerCase()}`);
      setInsight(response.data);
    } catch (err) {
      console.error("AI Insight Error:", err);
      setInsight({
        explanation: `We analyzed the recent ${metric} trend and found significant fluctuations in traffic sources.`,
        actions: ["Optimize landing page for mobile", "Review recently changed ad creatives", "A/B test the checkout button"],
        impact_score: "High"
      });
    } finally {
      setAiLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.get("http://localhost:8000/reports/export", { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'kpi_pilot_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download Error:", err);
      alert("Error generating report. Please try again.");
    }
  };

  return (
    <div className="flex min-h-screen bg-[#0f172a] text-slate-200">
      <Sidebar />
      
      <main className="flex-1 ml-64 p-8">
        <header className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold font-outfit text-white">Good Morning, Store Owner 👋</h1>
            <p className="text-slate-400">Here's what's happening with your store today.</p>
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-emerald-900/20"
            >
              <Download size={18} />
              Export PDF
            </button>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input 
                type="text" 
                placeholder="Search metrics..." 
                className="pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-blue-500/50 text-sm w-64"
              />
            </div>
            <button className="p-2 bg-slate-800/50 border border-slate-700/50 rounded-xl hover:bg-slate-800 transition-all relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-[#0f172a]"></span>
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Revenue" value="₺24,500" change="+12.5%" icon={<DollarSign className="text-emerald-400" />} onClick={() => handleExplain("Revenue")} />
          <StatCard title="Total Orders" value="142" change="+3.2%" icon={<ShoppingCart className="text-blue-400" />} onClick={() => handleExplain("Orders")} />
          <StatCard title="Conversion Rate" value="3.42%" change="-0.5%" trend="down" icon={<Users className="text-purple-400" />} onClick={() => handleExplain("Conversion Rate")} />
          <StatCard title="Average Order" value="₺172.50" change="+8.1%" icon={<TrendingUp className="text-amber-400" />} onClick={() => handleExplain("AOV")} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 p-8 bg-slate-800/20 border border-slate-700/50 rounded-3xl">
            <h3 className="text-xl font-bold font-outfit mb-8">Revenue Trend</h3>
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `₺${v}`} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '12px', color: '#f1f5f9' }} />
                  <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="lg:col-span-1 p-8 bg-gradient-to-br from-blue-600/10 to-emerald-600/10 border border-blue-500/20 rounded-3xl">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles size={18} className="text-blue-400" />
              <h3 className="text-xl font-bold font-outfit">AI Insights</h3>
            </div>
            <div className="space-y-4">
              <InsightItem title="Conversion Opportunity" description="Mobile conversion dropped. Check page speed." />
              <InsightItem title="Revenue Alert" description="Revenue is up 12% vs last week. High performing ads detected." />
            </div>
          </div>
        </div>
      </main>

      <Modal isOpen={isAiModalOpen} onClose={() => setIsAiModalOpen(false)} title={`AI Analysis: ${activeMetric}`}>
        {aiLoading ? (
          <div className="flex flex-col items-center py-12 gap-4">
            <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
            <p className="text-slate-400">Analyzing data...</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="p-4 bg-blue-600/10 border border-blue-500/20 rounded-2xl">
              <p className="text-white">{insight?.explanation}</p>
            </div>
            <div className="space-y-3">
              {insight?.actions.map((action: string, i: number) => (
                <div key={i} className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center text-xs font-bold">{i+1}</div>
                  <span className="text-slate-200 text-sm">{action}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

function StatCard({ title, value, change, icon, trend = "up", onClick }: any) {
  return (
    <div onClick={onClick} className="p-6 bg-slate-800/20 border border-slate-700/50 rounded-2xl hover:border-blue-500/50 transition-all group cursor-pointer">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-slate-800 rounded-lg group-hover:scale-110 transition-transform">{icon}</div>
        <span className={`text-xs font-bold px-2 py-1 rounded-full ${trend === "up" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>{change}</span>
      </div>
      <p className="text-slate-400 text-sm mb-1">{title}</p>
      <div className="flex items-end justify-between">
        <h3 className="text-2xl font-bold text-white font-outfit">{value}</h3>
        <span className="text-[10px] text-blue-400 font-bold uppercase flex items-center gap-1">Explain <Sparkles size={10} /></span>
      </div>
    </div>
  );
}

function InsightItem({ title, description }: any) {
  return (
    <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl">
      <h4 className="text-sm font-bold text-blue-400 mb-1">{title}</h4>
      <p className="text-xs text-slate-400">{description}</p>
    </div>
  );
}
