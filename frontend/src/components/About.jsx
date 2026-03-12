import { Link } from 'react-router-dom'

const PIPELINE = [
  {
    step: '1',
    name: 'Enter a Repo',
    desc: 'You type any public GitHub repository — or pick one of three presets. No login required.',
  },
  {
    step: '2',
    name: 'Fetch Issues',
    desc: 'The app pulls up to 100 real issues from the GitHub REST API, including title, body, labels, state, and timestamps.',
  },
  {
    step: '3',
    name: 'AI Classification',
    desc: 'Each issue is sent to a Groq-hosted LLM, which classifies it by type (bug, feature request, question, docs), priority (low, medium, high), sentiment, and writes a one-line summary.',
  },
  {
    step: '4',
    name: 'Store in PostgreSQL',
    desc: 'All issues and classifications are persisted to a relational database so results can be reloaded instantly without re-fetching or re-classifying.',
  },
  {
    step: '5',
    name: 'Analytics Dashboard',
    desc: 'SQL aggregation queries power five live charts: issue volume by type, priority distribution, open vs closed ratio, issues over time, and top labels by frequency.',
  },
  {
    step: '6',
    name: 'AI Triage Draft',
    desc: 'Click any open issue to stream an AI-drafted triage response — a ready-to-edit reply that acknowledges the issue and sets timeline expectations.',
  },
]

const HIGHLIGHTS = [
  'Full-stack Python + React application built from scratch with no starter templates',
  'LLM classification pipeline classifying each issue across four dimensions in parallel',
  'SQL analytics with GROUP BY, JOIN, UNNEST, DATE_TRUNC, and window functions',
  'Server-sent events (SSE) streaming AI draft responses word-by-word in real time',
  'PostgreSQL schema with indexed foreign keys across analysis_runs, issues, and classifications tables',
  'Multi-stage Docker build: Node builds the React frontend, Python serves everything via FastAPI',
  'Repo history — previously analyzed repos saved to DB and reloadable with one click',
  'Dark/light mode persisted to localStorage with zero flash on load',
]

const STACK = [
  { name: 'React + Vite', role: 'Frontend UI' },
  { name: 'Tailwind CSS', role: 'Styling' },
  { name: 'Recharts', role: 'Analytics charts' },
  { name: 'Python + FastAPI', role: 'Backend API' },
  { name: 'Groq (LLaMA 3.1)', role: 'AI / LLM' },
  { name: 'PostgreSQL', role: 'Data persistence' },
  { name: 'GitHub REST API', role: 'Issue ingestion' },
  { name: 'Docker', role: 'Containerized deploy' },
]

export default function About() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-12 pb-20">

      {/* Hero */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-3">About RepoSignal</h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
          RepoSignal turns any public GitHub repository into an instant analytics dashboard. It fetches real
          issues, classifies them with AI, and surfaces patterns — all powered by SQL and a live LLM pipeline.
          No spreadsheets, no manual tagging, no waiting.
        </p>
      </div>

      {/* Problem */}
      <section className="mb-12">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">The Problem It Solves</h3>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
          Open-source maintainers and engineering leads often have no easy way to understand the health of
          their issue backlog at a glance. Is it mostly bugs or feature requests? Are high-priority issues
          piling up? RepoSignal answers those questions in seconds — for any repo, with no setup.
        </p>
      </section>

      {/* Pipeline */}
      <section className="mb-12">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-5">How It Works</h3>
        <div className="flex flex-col gap-4">
          {PIPELINE.map((stage, i) => (
            <div key={stage.step} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-cyan-600 text-white text-sm font-bold flex items-center justify-center flex-shrink-0">
                  {stage.step}
                </div>
                {i < PIPELINE.length - 1 && (
                  <div className="w-px flex-1 bg-cyan-200 dark:bg-cyan-900 mt-2" />
                )}
              </div>
              <div className="pb-6">
                <div className="font-semibold text-gray-800 dark:text-gray-200 mb-1">{stage.name}</div>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{stage.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Highlights */}
      <section className="mb-12">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">What Was Built</h3>
        <ul className="space-y-2">
          {HIGHLIGHTS.map((item) => (
            <li key={item} className="flex gap-3 text-sm text-gray-600 dark:text-gray-400">
              <span className="text-cyan-500 mt-0.5 flex-shrink-0">&#10003;</span>
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* Stack */}
      <section className="mb-12">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Tech Stack</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STACK.map((item) => (
            <div
              key={item.name}
              className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-center"
            >
              <div className="text-sm font-semibold text-gray-800 dark:text-gray-200">{item.name}</div>
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-0.5">{item.role}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Links */}
      <section className="flex gap-4 flex-wrap">
        <Link
          to="/"
          className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-semibold rounded-xl transition-colors"
        >
          Try the App
        </Link>
        <a
          href="https://github.com/eholt723/reposignal"
          target="_blank"
          rel="noreferrer"
          className="px-5 py-2.5 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-semibold rounded-xl transition-colors"
        >
          View on GitHub
        </a>
      </section>

    </main>
  )
}
