import Link from "next/link";
import { LayoutDashboard, BarChart2, Zap, Settings, LogOut, Bell } from "lucide-react";

export const Sidebar = () => {
  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0f172a] flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-10">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white">P</div>
          <span className="text-xl font-bold font-outfit text-white">KPI Pilot</span>
        </div>

        <nav className="space-y-1">
          <SidebarItem icon={<LayoutDashboard size={20} />} label="Dashboard" href="/dashboard" active />
          <SidebarItem icon={<BarChart2 size={20} />} label="Metrics" href="/metrics" />
          <SidebarItem icon={<Zap size={20} />} label="Insights" href="/insights" />
          <SidebarItem icon={<Settings size={20} />} label="Settings" href="/settings" />
        </nav>
      </div>

      <div className="mt-auto p-6 border-t border-slate-800">
        <button className="flex items-center gap-3 text-slate-400 hover:text-white transition-colors text-sm font-medium w-full">
          <LogOut size={20} />
          Logout
        </button>
      </div>
    </aside>
  );
};

const SidebarItem = ({ icon, label, href, active = false }: { icon: React.ReactNode, label: string, href: string, active?: boolean }) => {
  return (
    <Link 
      href={href}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
        active 
          ? "bg-blue-600/10 text-blue-400 border border-blue-500/20" 
          : "text-slate-400 hover:text-white hover:bg-slate-800/50"
      }`}
    >
      {icon}
      {label}
    </Link>
  );
};
