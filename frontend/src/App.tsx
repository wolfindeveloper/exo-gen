import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import TopBar from './components/layout/TopBar'
import BottomNav from './components/layout/BottomNav'
import SettingsModal from './components/modals/SettingsModal'
import HangarPage from './pages/HangarPage'
import UniversePage from './pages/UniversePage'
import LaboratoryPage from './pages/LaboratoryPage'
import { ToastProvider } from './providers/ToastProvider'

/**
 * Анимация переходов между маршрутами.
 * Fade + slide: страница появляется снизу и становится прозрачной → видимой.
 */
const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -12 },
}

const pageTransition = {
  type: 'tween' as const,
  duration: 0.25,
  ease: 'easeInOut' as const,
}

/**
 * Обёртка маршрута с анимацией.
 * Каждая страница оборачивается в motion.div с AnimatePresence.
 */
function AnimatedRoute({ element }: { element: JSX.Element }): JSX.Element {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      transition={pageTransition}
      className="min-h-full"
    >
      {element}
    </motion.div>
  )
}

/**
 * Внутренний компонент App с доступом к useLocation.
 * AnimatePresence требует ключ (location.pathname) для отслеживания изменений маршрута.
 */
function AppRoutes({
  settingsOpen,
  onSettingsClick,
}: {
  settingsOpen: boolean
  onSettingsClick: () => void
}): JSX.Element {
  const location = useLocation()

  return (
    <>
      <TopBar onSettingsClick={onSettingsClick} />
      <main className="pt-28 pb-20">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route
              path="/"
              element={<Navigate to="/hangar" replace />}
            />
            <Route
              path="/hangar"
              element={<AnimatedRoute element={<HangarPage />} />}
            />
            <Route
              path="/universe"
              element={<AnimatedRoute element={<UniversePage />} />}
            />
            <Route
              path="/laboratory"
              element={<AnimatedRoute element={<LaboratoryPage />} />}
            />
          </Routes>
        </AnimatePresence>
      </main>
      <BottomNav />
      <SettingsModal isOpen={settingsOpen} onClose={() => onSettingsClick()} />
    </>
  )
}

function App(): JSX.Element {
  const [settingsOpen, setSettingsOpen] = useState(false)

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-cosmic-bg">
        <ToastProvider />
        <AppRoutes
          settingsOpen={settingsOpen}
          onSettingsClick={() => setSettingsOpen(!settingsOpen)}
        />
      </div>
    </BrowserRouter>
  )
}

export default App
