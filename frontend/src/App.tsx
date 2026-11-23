import { Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { HealthProvider } from './context/HealthContext';
import { DashboardPage } from './pages/DashboardPage';
import { MessagesPage } from './pages/MessagesPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { PatientDetailPage } from './pages/PatientDetailPage';
import { PatientsPage } from './pages/PatientsPage';
import { SystemPage } from './pages/SystemPage';
import { TriagePage } from './pages/TriagePage';

export function App() {
  return (
    <HealthProvider>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="pacientes" element={<PatientsPage />} />
          <Route path="pacientes/ficha" element={<PatientDetailPage />} />
          <Route path="pacientes/:patientId" element={<PatientDetailPage />} />
          <Route path="mensagens" element={<MessagesPage />} />
          <Route path="triagem" element={<TriagePage />} />
          <Route path="sistema" element={<SystemPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </HealthProvider>
  );
}
