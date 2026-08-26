import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Home } from './pages/Home'
import { Play } from './pages/Play'

export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/play/:id" element={<Play />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
