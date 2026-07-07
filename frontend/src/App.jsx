import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

function ScoreBadge({ score }) {
  if (score === null || score === undefined) return <span className="text-gray-500">N/A</span>
  const color = score >= 75 ? "text-green-400" : score >= 50 ? "text-yellow-400" : "text-red-400"
  return <span className={`font-bold ${color}`}>{score}</span>
}

function SiteRow({ site, onClick }) {
  return (
    <tr
      onClick={() => onClick(site)}
      className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition"
    >
      <td className="py-3 px-4 text-white">{site.domain}</td>
      <td className="py-3 px-4 text-gray-400 text-sm truncate max-w-[200px]">{site.page_title || "—"}</td>
      <td className="py-3 px-4 text-gray-400">{site.response_time ? `${site.response_time}s` : "—"}</td>
      <td className="py-3 px-4"><ScoreBadge score={site.performance_score} /></td>
      <td className="py-3 px-4"><ScoreBadge score={site.seo_score} /></td>
      <td className="py-3 px-4"><ScoreBadge score={site.accessibility_score} /></td>
    </tr>
  )
}

function SiteModal({ site, onClose }) {
  if (!site) return null
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-white text-xl font-bold">{site.domain}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">✕</button>
        </div>
        <p className="text-gray-400 text-sm mb-4">{site.meta_description || "No description available"}</p>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white/5 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">Performance</p>
            <ScoreBadge score={site.performance_score} />
          </div>
          <div className="bg-white/5 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">SEO</p>
            <ScoreBadge score={site.seo_score} />
          </div>
          <div className="bg-white/5 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">Accessibility</p>
            <ScoreBadge score={site.accessibility_score} />
          </div>
        </div>
        {site.ai_summary && (
          <div className="bg-white/5 rounded-xl p-4 mb-4">
            <p className="text-gray-400 text-xs mb-2">AI Summary</p>
            <p className="text-white text-sm">{site.ai_summary}</p>
          </div>
        )}
        {site.headers && JSON.parse(site.headers).length > 0 && (
          <div className="bg-white/5 rounded-xl p-4 mb-4">
            <p className="text-gray-400 text-xs mb-2">Headers</p>
            {JSON.parse(site.headers).slice(0, 5).map((h, i) => (
              <p key={i} className="text-white text-sm mb-1">
                <span className="text-blue-400 font-bold">{h.tag.toUpperCase()}</span> — {h.text}
              </p>
            ))}
          </div>
        )}
        {site.structured_data && JSON.parse(site.structured_data).length > 0 && (
          <div className="bg-white/5 rounded-xl p-4">
            <p className="text-gray-400 text-xs mb-2">Structured Data</p>
            <pre className="text-white text-xs overflow-x-auto">
              {JSON.stringify(JSON.parse(site.structured_data), null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

function ProgressModal({ onClose, scraped, totalCSV, progress }) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-white text-lg font-bold">Scraping Details</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">✕</button>
        </div>
        <div className="space-y-4">

          <div className="bg-white/5 rounded-xl p-4">
            <p className="text-gray-400 text-xs mb-1">Total scraped</p>
            <p className="text-white font-bold text-lg">{scraped}/{totalCSV}</p>
            <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
              <div
                className="bg-white h-1.5 rounded-full transition-all"
                style={{ width: `${totalCSV ? (scraped / totalCSV) * 100 : 0}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white/5 rounded-xl p-4">
            <p className="text-gray-400 text-xs mb-1">With data</p>
            <p className="text-blue-400 font-bold text-lg">{progress.complete}/{totalCSV}</p>
            <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
              <div
                className="bg-blue-400 h-1.5 rounded-full transition-all"
                style={{ width: `${totalCSV ? (progress.complete / totalCSV) * 100 : 0}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <p className="text-gray-400 text-xs mb-2">Live Activity</p>
            {progress.pass === "Idle" ? (
              <p className="text-gray-500 font-bold">⏸ Scraper is stopped</p>
            ) : progress.pass === "Complete!" ? (
              <p className="text-blue-400 font-bold">✓ All done!</p>
            ) : (
              <>
                <p className="text-green-400 font-bold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse inline-block"></span>
                  {progress.pass}
                </p>
                <p className="text-white text-sm mt-2 font-mono truncate">{progress.domain || "—"}</p>
                <p className="text-gray-400 text-xs mt-1">{progress.current} of {progress.total} sites</p>
                <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
                  <div
                    className="bg-green-400 h-1.5 rounded-full transition-all"
                    style={{ width: `${progress.total ? (progress.current / progress.total) * 100 : 0}%` }}
                  ></div>
                </div>
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}

function IndustrySection({ industry, sites, onSiteClick }) {
  return (
    <div className="mb-10">
      <h2 className="text-white text-lg font-semibold mb-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
        {industry}
        <span className="text-gray-500 text-sm font-normal">({sites.length} sites)</span>
      </h2>
      <div className="bg-[#111] border border-white/10 rounded-2xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 text-gray-500 text-xs uppercase">
              <th className="py-3 px-4 text-left">Domain</th>
              <th className="py-3 px-4 text-left">Title</th>
              <th className="py-3 px-4 text-left">Response</th>
              <th className="py-3 px-4 text-left">Perf</th>
              <th className="py-3 px-4 text-left">SEO</th>
              <th className="py-3 px-4 text-left">Access</th>
            </tr>
          </thead>
          <tbody>
            {sites.map(site => (
              <SiteRow key={site.id} site={site} onClick={onSiteClick} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function App() {
  const [sites, setSites] = useState([])
  const [industries, setIndustries] = useState([])
  const [selectedIndustry, setSelectedIndustry] = useState("All")
  const [selectedSite, setSelectedSite] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scraped, setScraped] = useState(0)
  const [totalCSV, setTotalCSV] = useState(0)
  const [progress, setProgress] = useState({ current: 0, total: 0, domain: "", pass: "Idle", retry_count: 0, complete: 0, retries: [] })
  const [showProgress, setShowProgress] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sitesRes, industriesRes, statusRes, progressRes] = await Promise.all([
          axios.get(`${API}/sites`),
          axios.get(`${API}/industries`),
          axios.get(`${API}/status`),
          axios.get(`${API}/progress`)
        ])
        setSites(sitesRes.data)
        setIndustries(["All", ...industriesRes.data])
        setScraped(statusRes.data.scraped)
        setTotalCSV(statusRes.data.total)
        setProgress({ ...progressRes.data, complete: statusRes.data.complete })
      } catch (err) {
        console.error("Failed to fetch data", err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  const filteredSites = selectedIndustry === "All"
    ? sites
    : sites.filter(s => s.industry === selectedIndustry)

  const groupedByIndustry = filteredSites.reduce((acc, site) => {
    if (!acc[site.industry]) acc[site.industry] = []
    acc[site.industry].push(site)
    return acc
  }, {})

  const sitesWithData = sites.filter(s => s.performance_score && s.performance_score > 0)
  const avgPerformance = sitesWithData.length ? Math.round(sitesWithData.reduce((a, s) => a + s.performance_score, 0) / sitesWithData.length) : 0
  const avgSeo = sitesWithData.length ? Math.round(sitesWithData.reduce((a, s) => a + (s.seo_score || 0), 0) / sitesWithData.length) : 0

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="max-w-7xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Nigeria Web Intelligence</h1>
          <p className="text-gray-500 mt-1">Top Nigerian websites ranked by industry and performance</p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-3 gap-4 mb-8">

          {/* Scraping Status Card */}
          <div
            className="bg-[#111] border border-white/10 rounded-2xl p-5 cursor-pointer hover:border-white/25 transition"
            onClick={() => setShowProgress(true)}
          >
            <p className="text-gray-400 text-sm">Scraping Status</p>
            <p className="text-white text-2xl font-bold mt-1">{scraped}/{totalCSV}</p>
            <p className="text-blue-400 text-xs mt-1">✓ With data: {progress.complete}/{totalCSV}</p>
            <p className={`text-xs mt-1 flex items-center gap-1 ${
              progress.pass === "Idle" ? "text-gray-400" :
              progress.pass === "Complete!" ? "text-blue-400" : "text-green-400"
            }`}>
              <span className={`w-2 h-2 rounded-full inline-block ${
                progress.pass === "Idle" ? "bg-gray-400" :
                progress.pass === "Complete!" ? "bg-blue-400" :
                "bg-green-400 animate-pulse"
              }`}></span>
              {progress.pass === "Complete!" ? "Finished!" :
               progress.pass === "Idle" ? "Scraper is stopped" :
               "Actively scraping..."} · tap for details
            </p>
          </div>

          <div className="bg-[#111] border border-white/10 rounded-2xl p-5">
            <p className="text-gray-400 text-sm">Avg Performance</p>
            <p className="text-2xl font-bold mt-1"><ScoreBadge score={avgPerformance} /></p>
          </div>

          <div className="bg-[#111] border border-white/10 rounded-2xl p-5">
            <p className="text-gray-400 text-sm">Avg SEO</p>
            <p className="text-2xl font-bold mt-1"><ScoreBadge score={avgSeo} /></p>
          </div>

        </div>

        {/* Industry Filter */}
        <div className="flex gap-2 flex-wrap mb-8">
          {industries.map(ind => (
            <button
              key={ind}
              onClick={() => setSelectedIndustry(ind)}
              className={`px-4 py-1.5 rounded-full text-sm transition ${
                selectedIndustry === ind
                  ? "bg-blue-600 text-white"
                  : "bg-white/5 text-gray-400 hover:bg-white/10"
              }`}
            >
              {ind}
            </button>
          ))}
        </div>

        {/* Sites by Industry */}
        {loading ? (
          <p className="text-gray-500">Loading sites...</p>
        ) : Object.keys(groupedByIndustry).length === 0 ? (
          <p className="text-gray-500">Loading data... Make sure the backend is running.</p>
        ) : (
          Object.entries(groupedByIndustry).map(([industry, sites]) => (
            <IndustrySection
              key={industry}
              industry={industry}
              sites={sites}
              onSiteClick={setSelectedSite}
            />
          ))
        )}
      </div>

      <SiteModal site={selectedSite} onClose={() => setSelectedSite(null)} />

      {showProgress && (
        <ProgressModal
          onClose={() => setShowProgress(false)}
          scraped={scraped}
          totalCSV={totalCSV}
          progress={progress}
        />
      )}
    </div>
  )
}