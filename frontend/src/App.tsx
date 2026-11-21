import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { VoiceAssistantPage } from './pages/VoiceAssistantPage';
import { DashboardPage } from './pages/DashboardPage';
import { FollowUpsPage } from './pages/FollowUpsPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { AuthPage } from './pages/AuthPage';
import { User } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('landing');
  const [user, setUser] = useState<User | null>({
    id: 1,
    email: 'asha.shweta@karnataka.gov.in',
    full_name: 'Shweta Patil (ASHA Worker)',
    role: 'ASHA_WORKER',
  });

  const handleDemoLogin = async () => {
    try {
      const res = await api.demoLogin();
      setUser(res.user);
      setCurrentTab('dashboard');
    } catch (e) {
      console.error(e);
      // Fallback
      setUser({
        id: 1,
        email: 'asha.shweta@karnataka.gov.in',
        full_name: 'Shweta Patil (ASHA Worker)',
        role: 'ASHA_WORKER',
      });
      setCurrentTab('dashboard');
    }
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentTab('landing');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#031410] text-slate-100 selection:bg-[#00f5d4]/30 selection:text-[#00f5d4]">
      {/* Navigation Header */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        user={user}
        onDemoLogin={handleDemoLogin}
        onLogout={handleLogout}
      />

      {/* Main Page Content */}
      <main className="flex-1 flex flex-col">
        {currentTab === 'landing' && (
          <LandingPage
            onStartRecording={() => setCurrentTab('voice')}
            onExploreDashboard={() => setCurrentTab('dashboard')}
          />
        )}

        {currentTab === 'voice' && <VoiceAssistantPage />}

        {currentTab === 'dashboard' && (
          <DashboardPage
            onNavigateToVoice={() => setCurrentTab('voice')}
            onNavigateToFollowups={() => setCurrentTab('followups')}
          />
        )}

        {currentTab === 'followups' && <FollowUpsPage />}

        {currentTab === 'architecture' && <ArchitecturePage />}

        {currentTab === 'auth' && (
          <AuthPage
            onSuccess={(loggedUser) => {
              setUser(loggedUser);
              setCurrentTab('dashboard');
            }}
          />
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default App;
