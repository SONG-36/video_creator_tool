import { Link, Route, Routes } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { GenerationResultReviewPage } from './pages/GenerationResultReviewPage'
import { ProductionPage } from './pages/ProductionPage'
import { StoryboardReviewPage } from './pages/StoryboardReviewPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route
        path="/storyboards/:storyboardId/review"
        element={<StoryboardReviewPage />}
      />
      <Route path="/shots/:shotId/production" element={<ProductionPage />} />
      <Route
        path="/generation-results/:resultId/review"
        element={<GenerationResultReviewPage />}
      />
      <Route
        path="*"
        element={
          <div className="flex min-h-screen items-center justify-center px-4">
            <div className="rounded-[1.8rem] border border-white/70 bg-white/80 p-8 text-center shadow-[0_28px_80px_-50px_rgba(20,45,38,0.7)]">
              <p className="text-sm uppercase tracking-[0.24em] text-slate-500">
                Page Not Found
              </p>
              <h1 className="mt-3 text-3xl font-bold tracking-[-0.04em] text-slate-950">
                当前页面不存在
              </h1>
              <Link
                to="/"
                className="mt-6 inline-flex rounded-full bg-emerald-900 px-5 py-3 text-sm font-semibold text-white"
              >
                返回 Dashboard
              </Link>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export default App
