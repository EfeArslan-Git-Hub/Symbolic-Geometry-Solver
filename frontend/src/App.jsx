import { useState, useEffect } from 'react'
import axios from 'axios'
import 'katex/dist/katex.min.css'
import { BlockMath, InlineMath } from 'react-katex'
import { motion, AnimatePresence } from 'framer-motion'
import { Calculator, ChevronRight, Sparkles, AlertCircle, Clock, RotateCcw, Menu, X, Box, Activity, GraduationCap, ExternalLink } from 'lucide-react'
import Plot from 'react-plotly.js'

function App() {
  const [problem, setProblem] = useState('')
  const [solution, setSolution] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // History State
  const [history, setHistory] = useState([])
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [isMobile, setIsMobile] = useState(false)

  // Mobile Detection & Init
  useEffect(() => {
    const checkMobile = () => {
      const isMob = window.innerWidth < 768
      setIsMobile(isMob)
      if (isMob) setIsSidebarOpen(false)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Load history on mount
  useEffect(() => {
    const saved = localStorage.getItem('math_history')
    if (saved) {
      setHistory(JSON.parse(saved))
    }
  }, [])

  const addToHistory = (query) => {
    const newHistory = [query, ...history.filter(h => h !== query)].slice(0, 15)
    setHistory(newHistory)
    localStorage.setItem('math_history', JSON.stringify(newHistory))
  }

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('math_history');
  }

  const handleSubmit = async (e) => {
    e && e.preventDefault()
    if (!problem.trim()) return

    setLoading(true)
    setError(null)
    setSolution(null)

    // On mobile, auto-close sidebar
    if (isMobile) setIsSidebarOpen(false)

    try {
      // Use environment variable for API URL (defaults to localhost for dev)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

      const response = await axios.post(`${apiUrl}/solve`, {
        problem: problem
      })
      setSolution(response.data)
      addToHistory(problem)
    } catch (err) {
      console.error(err)
      setError(err.message ? `Error: ${err.message}` : 'Connection to Solver Engine failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit()
    }
  }

  const handleChipClick = (ex) => {
    setProblem(ex)
    if (isMobile) setIsSidebarOpen(false)
  }

  const categories = [
    {
      name: 'Physics 🚀',
      examples: [
        'projectile velocity 50 angle 45',
        'projectile velocity 100 angle 30',
        'projectile velocity 20 angle 60'
      ]
    },
    {
      name: 'Calculus ∫',
      examples: [
        'derivative x**3 - 2*x + 5',
        'derivative sin(x) * x',
        'derivative (x+1)/(x-1)',
        'integrate x**2',
        'integrate cos(x)',
        'integrate x * exp(x)'
      ]
    },
    {
      name: 'Algebra 📐',
      examples: [
        'x**2 - 9 = 0',
        '3*x + 5 = 20',
        'x**3 - x = 0',
        'simplify (x+2)**2',
        'expand (x+1)*(x-1)'
      ]
    },
    {
      name: 'Geometry & 3D 🧊',
      examples: [
        'hypotenuse sides 3 4',
        'hypotenuse sides 5 12',
        'sphere radius 5',
        'distance 3d (0,0,0) (1,1,1)'
      ]
    },
    {
      name: 'Metric Spaces 📏',
      examples: [
        'distance euclidean (0,0) (3,4)',
        'distance taxicab (0,0) (3,4)',
        'distance chebyshev (0,0) (3,4)'
      ]
    }
  ]

  // Helper to parse step text with Markdown-like bold and Math
  const renderStepContent = (text) => {
    const parts = text.split('\\\\');
    return (
      <div className="flex flex-col gap-1">
        {parts.map((part, i) => {
          const boldParts = part.split(/(\*\*.*?\*\*)/g);
          return (
            <div key={i} className="text-xs md:text-sm text-slate-300">
              {boldParts.map((sub, j) => {
                if (sub.startsWith('**') && sub.endsWith('**')) {
                  return <strong key={j} className="text-purple-300 font-bold">{sub.slice(2, -2)}</strong>
                }
                if (sub.includes('$')) {
                  const mathParts = sub.split('$');
                  return mathParts.map((m, k) => k % 2 === 1 ? <span key={k} className="bg-white/5 px-1 rounded mx-1"><InlineMath math={m} /></span> : m);
                }
                return sub;
              })}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900 text-white font-sans selection:bg-purple-500 selection:text-white flex overflow-hidden">

      {/* Mobile Backdrop */}
      <AnimatePresence>
        {isMobile && isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setIsSidebarOpen(false)}
            className="absolute inset-0 bg-black/60 z-30 backdrop-blur-sm"
          />
        )}
      </AnimatePresence>

      {/* Sidebar (History) - Responsive */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0, x: isMobile ? -280 : 0 }}
            animate={{ width: 280, opacity: 1, x: 0 }}
            exit={{ width: 0, opacity: 0, x: isMobile ? -280 : 0 }}
            className={`h-screen bg-black/40 backdrop-blur-xl border-r border-white/10 flex-shrink-0 flex flex-col z-40 ${isMobile ? 'absolute top-0 left-0 shadow-2xl' : 'relative'}`}
          >
            <div className="p-6 border-b border-white/5 flex items-center justify-between">
              <h2 className="text-lg font-bold flex items-center gap-2 text-purple-300">
                <Clock className="w-5 h-5" /> History
              </h2>
              <div className="flex items-center gap-2">
                <button onClick={clearHistory} className="text-xs text-slate-500 hover:text-red-400 transition-colors">Clear</button>
                {/* Mobile Close Button */}
                {isMobile && (
                  <button onClick={() => setIsSidebarOpen(false)} className="p-1 hover:bg-white/10 rounded-full transition-colors">
                    <X className="text-white/70 w-5 h-5" />
                  </button>
                )}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {history.length === 0 ? (
                <div className="text-center text-slate-500 text-sm mt-10">
                  No recent calculations.
                </div>
              ) : (
                history.map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleChipClick(item)}
                    className="group p-3 rounded-lg hover:bg-white/5 cursor-pointer transition-colors border border-transparent hover:border-white/5"
                  >
                    <div className="text-xs md:text-sm font-mono truncate text-slate-300 group-hover:text-purple-300">{item}</div>
                  </div>
                ))
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-y-auto relative w-full">

        {/* Top Bar (Toggle Sidebar & Portfolio) */}
        <div className="w-full flex justify-between items-center p-4 z-20 sticky top-0 bg-transparent pointer-events-none">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 glass-panel rounded-full hover:bg-white/20 transition-colors pointer-events-auto shadow-lg"
          >
            {isSidebarOpen && !isMobile ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <a
            href="https://efe-arslan-portfolio.vercel.app/"
            target="_blank"
            rel="noopener noreferrer"
            className="glass-panel p-2 px-4 rounded-full flex items-center gap-2 hover:bg-white/20 transition-colors text-xs font-semibold text-slate-300 hover:text-white pointer-events-auto shadow-lg"
          >
            <span className="hidden md:inline">Created by Efe</span>
            <span className="md:hidden">Efe A.</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        {/* Header */}
        <header className="px-4 pb-0 text-center mt-2 md:mt-6">
          <div className="glass-panel inline-flex items-center gap-3 px-4 py-1.5 md:px-6 md:py-2 rounded-full mb-4">
            <GraduationCap className="text-yellow-400 w-4 h-4" />
            <span className="text-[10px] md:text-sm font-semibold tracking-wider text-slate-300 uppercase">Math Tutor v5.0</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 pb-2">
            Symbolic Solver
          </h1>
        </header>

        <main className="flex-1 flex flex-col md:flex-row gap-6 p-4 md:p-8 max-w-7xl mx-auto w-full items-start">

          {/* INPUT PANEL */}
          <motion.div
            layout
            className="w-full md:w-[450px] flex-shrink-0 space-y-6"
          >
            <div className="glass-card p-4 md:p-6 rounded-2xl border border-white/10 bg-white/5 shadow-2xl">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Expression</label>
                  </div>
                  <textarea
                    value={problem}
                    onChange={(e) => setProblem(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Try: 'hypotenuse sides 5 12'..."
                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl p-3 md:p-4 text-lg md:text-xl font-mono focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all resize-none h-24 md:h-32 placeholder-slate-600 text-white"
                  />
                  <div className="hidden md:block text-right text-[10px] text-slate-500 mt-1">Ctrl + Enter to solve</div>
                </div>

                <button
                  type="submit"
                  disabled={loading || !problem.trim()}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold py-3 rounded-xl shadow-lg transform active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-t-transparent border-white"></div> : <>Analyze <ChevronRight className="w-5 h-5" /></>}
                </button>
              </form>
            </div>

            {/* Categories & Examples */}
            <div className="space-y-4 md:max-h-[500px] overflow-x-auto md:overflow-visible">
              {categories.map((cat) => (
                <div key={cat.name}>
                  <h3 className="text-xs font-bold text-slate-500 uppercase mb-2 ml-1 flex items-center gap-2">
                    {cat.name}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {cat.examples.map((ex) => (
                      <button
                        key={ex}
                        onClick={() => handleChipClick(ex)}
                        className="text-[10px] md:text-xs font-mono bg-white/5 hover:bg-purple-500/20 border border-white/5 hover:border-purple-500/30 px-2.5 py-1.5 rounded-full transition-colors text-slate-300 whitespace-nowrap"
                      >
                        {ex}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* OUTPUT PANEL */}
          <motion.div
            layout
            className="flex-1 w-full min-w-0"
          >
            <AnimatePresence mode='wait'>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="glass-card bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex items-center gap-3 text-red-200 mb-4"
                >
                  <AlertCircle className="w-5 h-5" /> {error}
                </motion.div>
              )}

              {solution ? (
                <motion.div
                  key="solution"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-6"
                >
                  {/* Solution Result */}
                  <div className="glass-card bg-gradient-to-b from-slate-800/80 to-slate-900/80 border border-white/10 backdrop-blur-md p-6 md:p-8 rounded-2xl shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10"><Calculator className="w-16 h-16 md:w-24 md:h-24" /></div>
                    <h2 className="text-sm font-bold text-slate-400 uppercase mb-4 border-b border-white/5 pb-2">Result</h2>
                    <div className="text-xl md:text-3xl py-2 overflow-x-auto scrollbar-thin scrollbar-thumb-white/10">
                      <BlockMath math={solution.solution_latex} />
                    </div>
                  </div>

                  <div className="flex flex-col-reverse md:grid md:grid-cols-2 gap-6">
                    {/* Enhanced Steps (Timeline) */}
                    {solution.steps && (
                      <div className="glass-card bg-white/5 border border-white/5 p-4 md:p-6 rounded-2xl">
                        <h3 className="text-xs md:text-sm font-bold text-slate-400 uppercase mb-6 flex items-center gap-2">
                          <GraduationCap className="w-4 h-4 text-yellow-400" /> Explanation
                        </h3>
                        <div className="space-y-0 relative border-l border-white/10 ml-3">
                          {solution.steps.map((step, idx) => (
                            <div key={idx} className="relative pl-6 md:pl-8 pb-8 last:pb-0">
                              {/* Timeline Dot */}
                              <span className="absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full bg-purple-500 border border-purple-300 shadow-[0_0_10px_rgba(168,85,247,0.5)]"></span>

                              {/* Content */}
                              <div className="leading-relaxed">
                                {renderStepContent(step)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Interactive Plot */}
                    {solution.plotData && (
                      <div className="glass-card bg-white/5 p-2 rounded-2xl border border-white/10 self-start w-full">
                        <h3 className="text-xs font-bold text-slate-500 uppercase mb-2 ml-2 mt-2">Interactive Visual</h3>
                        <div className="w-full h-64 md:h-[400px]">
                          <Plot
                            data={solution.plotData.data}
                            layout={{
                              ...solution.plotData.layout,
                              width: undefined,
                              height: undefined, // Let parent div control height
                              autosize: true,
                              margin: { t: 30, r: 10, l: 30, b: 30 },
                              paper_bgcolor: 'rgba(0,0,0,0)',
                              plot_bgcolor: 'rgba(0,0,0,0)',
                              font: { color: 'white' }
                            }}
                            config={{ responsive: true, displayModeBar: false }}
                            className="w-full h-full rounded-xl"
                            useResizeHandler={true}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ) : (
                !loading && !error && (
                  <div className="h-48 md:h-full min-h-[200px] md:min-h-[400px] flex flex-col items-center justify-center text-slate-600 space-y-4 border-2 border-dashed border-slate-800 rounded-3xl mx-4 md:mx-0">
                    <div className="p-4 bg-slate-800/50 rounded-full">
                      <RotateCcw className="w-6 h-6 md:w-8 md:h-8 opacity-40" />
                    </div>
                    <p className="text-sm md:text-lg font-medium">Waiting for input...</p>
                    <p className="text-[10px] md:text-xs opacity-50">Select an example or type your own</p>
                  </div>
                )
              )}
            </AnimatePresence>
          </motion.div>

        </main>
      </div>
    </div>
  )
}

export default App
