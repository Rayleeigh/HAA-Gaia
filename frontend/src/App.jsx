import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import VMList from './pages/VMList'
import CreateVM from './pages/CreateVM'
import Templates from './pages/Templates'
import Providers from './pages/Providers'
import ProviderSettings from './pages/ProviderSettings'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/vms" element={<VMList />} />
          <Route path="/vms/create" element={<CreateVM />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/providers" element={<Providers />} />
          <Route path="/providers/settings" element={<ProviderSettings />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
