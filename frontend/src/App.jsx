import React, { useState } from 'react'
import { Upload, BarChart3, FilePieChart, Download, Activity, FileText, CheckCircle2, AlertCircle } from 'lucide-react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'

function App() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleFileUpload = async (event) => {
        const file = event.target.files[0]
        if (!file) return

        setLoading(true)
        setError(null)
        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await axios.post('/api/upload', formData)
            setData(response.data)
        } catch (err) {
            setError('Dosya yüklenirken bir hata oluştu. Lütfen formatı kontrol edin.')
        } finally {
            setLoading(false)
        }
    }

    const downloadReport = async () => {
        try {
            const response = await axios.get('/api/report', { responseType: 'blob' })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'satis_raporu.pdf')
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (err) {
            alert('Rapor indirilirken bir hata oluştu.')
        }
    }

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-4 md:p-8">
            <header className="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                        KPI Analiz Sistemi
                    </h1>
                    <p className="text-slate-400 mt-1">Veri odaklı satış kararları alın.</p>
                </div>
                {data && (
                    <button
                        onClick={downloadReport}
                        className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-emerald-900/20"
                    >
                        <Download size={20} />
                        PDF Raporu İndir
                    </button>
                )}
            </header>

            <main className="max-w-7xl mx-auto flex flex-col gap-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Upload & Instructions */}
                    <div className="lg:col-span-1 flex flex-col gap-6">
                        <section className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-3xl">
                            <div className="flex items-center gap-3 mb-6">
                                <Upload className="text-blue-400" size={24} />
                                <h2 className="text-xl font-semibold">Veri Yükleme</h2>
                            </div>

                            <label className="group relative border-2 border-dashed border-slate-700 rounded-2xl p-8 text-center hover:border-blue-400/50 transition-all cursor-pointer block bg-slate-900/20">
                                <input type="file" className="hidden" onChange={handleFileUpload} accept=".csv,.xlsx,.xls" />
                                <div className="flex flex-col items-center">
                                    <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                        <FileText className="text-blue-400" size={32} />
                                    </div>
                                    <p className="font-medium text-slate-300">Dosya Seçin</p>
                                    <p className="text-xs text-slate-500 mt-2">CSV, Excel (max 10MB)</p>
                                </div>
                            </label>

                            {loading && (
                                <div className="mt-4 flex items-center gap-3 text-blue-400 text-sm animate-pulse">
                                    <Activity size={16} /> Analiz ediliyor...
                                </div>
                            )}
                            {error && (
                                <div className="mt-4 flex items-center gap-3 text-red-400 text-sm bg-red-400/10 p-3 rounded-lg">
                                    <AlertCircle size={16} /> {error}
                                </div>
                            )}
                            {data && !loading && (
                                <div className="mt-4 flex items-center gap-3 text-emerald-400 text-sm bg-emerald-400/10 p-3 rounded-lg">
                                    <CheckCircle2 size={16} /> Veri başarıyla işlendi.
                                </div>
                            )}
                        </section>

                        <section className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-3xl">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Gerekli Sütunlar</h3>
                            <ul className="space-y-2">
                                {['Date', 'Product', 'Category', 'Quantity', 'UnitPrice'].map(col => (
                                    <li key={col} className="flex items-center gap-2 text-sm text-slate-300">
                                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                                        <code>{col}</code>
                                    </li>
                                ))}
                            </ul>
                        </section>
                    </div>

                    {/* KPI Dashboard */}
                    <div className="lg:col-span-2 flex flex-col gap-6">
                        <AnimatePresence mode="wait">
                            {data ? (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="grid grid-cols-1 md:grid-cols-2 gap-4"
                                >
                                    <StatCard icon={<Activity className="text-blue-400" />} label="Toplam Gelir" value={`₺${data.kpis.total_revenue.toLocaleString('tr-TR')}`} />
                                    <StatCard icon={<FilePieChart className="text-emerald-400" />} label="Toplam Sipariş" value={data.kpis.total_orders} />
                                    <StatCard icon={<BarChart3 className="text-purple-400" />} label="Ort. Sipariş" value={`₺${data.kpis.avg_order_value.toLocaleString('tr-TR', { maximumFractionDigits: 2 })}`} />
                                    <StatCard icon={<Activity className="text-amber-400" />} label="Toplam Ürün" value={data.kpis.total_items} />
                                </motion.div>
                            ) : (
                                <div className="h-full min-h-[400px] flex items-center justify-center border border-slate-700/50 rounded-3xl bg-slate-900/20 text-slate-500 italic">
                                    Henüz veri yüklenmedi. Başlamak için bir dosya yükleyin.
                                </div>
                            )}
                        </AnimatePresence>

                        {data && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <ChartWrapper title="Satış Trendi">
                                    <img src={`data:image/png;base64,${data.charts.trend}`} alt="Trend" className="w-full h-auto" />
                                </ChartWrapper>
                                <ChartWrapper title="Kategori Bazlı Dağılım">
                                    <img src={`data:image/png;base64,${data.charts.category}`} alt="Category" className="w-full h-auto" />
                                </ChartWrapper>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}

function StatCard({ icon, label, value }) {
    return (
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-3xl hover:border-slate-600 transition-all">
            <div className="mb-4">{icon}</div>
            <p className="text-slate-400 text-sm font-medium">{label}</p>
            <h3 className="text-3xl font-bold mt-1 tracking-tight text-white">{value}</h3>
        </div>
    )
}

function ChartWrapper({ title, children }) {
    return (
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-3xl overflow-hidden">
            <h3 className="text-lg font-semibold mb-4 text-slate-300">{title}</h3>
            {children}
        </div>
    )
}

export default App
