'use client';

import { BuildingsContent } from './components/BuildingsContent';
import { NotesTooltip } from './components/NotesTooltip';
import { RefreshButton } from './components/RefreshButton';
import { useState, useEffect, useCallback } from 'react';
import type { OpenClassroomsResponse } from './types/buildings';

export default function Home() {
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [cooldownRemaining, setCooldownRemaining] = useState<number | null>(null);
  const [cooldownExpiresAt, setCooldownExpiresAt] = useState<number | null>(null);
  const [isCooldownLoading, setIsCooldownLoading] = useState<boolean>(true);
  const [buildings, setBuildings] = useState<OpenClassroomsResponse | null>(null);
  const [buildingsError, setBuildingsError] = useState<string | null>(null);

  const fetchCooldownStatus = useCallback(async () => {
    setIsCooldownLoading(true);
    try {
      const response = await fetch('/api/cooldown-status');
      if (response.ok) {
        const data = await response.json();
        if (data.in_cooldown) {
          const expiresAt = Date.now() + data.remaining_minutes * 60 * 1000;
          setCooldownExpiresAt(expiresAt);
          setCooldownRemaining(data.remaining_minutes);
        } else {
          setCooldownRemaining(null);
          setCooldownExpiresAt(null);
        }
      }
    } catch (error) {
      console.error('Failed to fetch cooldown status:', error);
    }
    finally {
      setIsCooldownLoading(false);
    }
  }, []);

  const fetchLastUpdated = useCallback(async () => {
    try {
      const response = await fetch('/api/open-classrooms');
      if (response.ok) {
        const data = await response.json();
        setBuildings(data.buildings);
        setBuildingsError(null);
        const incomingTs: string | null = data.last_updated ?? null;
        if (incomingTs) {
          if (!lastUpdated || new Date(incomingTs) >= new Date(lastUpdated)) {
            setLastUpdated(incomingTs);
          }
        }
        
        if (data.last_updated) {
          await fetchCooldownStatus();
        }
      }
    } catch (error) {
      console.error('Failed to fetch last updated time:', error);
      setBuildingsError('Failed to load classrooms. Please try again later.');
    }
  }, [fetchCooldownStatus, lastUpdated]);

  const handleRefresh = async () => {
    if (cooldownRemaining && cooldownRemaining > 0) {
      return; // Don't allow refresh during cooldown
    }
    
    setIsRefreshing(true);
    setCooldownRemaining(null);
    
    try {
      const response = await fetch('/api/refresh', {
        method: 'POST',
      });
      
      if (response.ok) {
        const data = await response.json();
        setLastUpdated(data.timestamp);
        // Refetch cooldown and classrooms
        await fetchCooldownStatus();
        await fetchLastUpdated();
      } else {
        const errorData = await response.json();
        // Extract cooldown time from error message
        const cooldownMatch = errorData.error?.match(/(\d+\.?\d*)\s+more\s+minutes/);
        if (cooldownMatch) {
          const minutes = parseFloat(cooldownMatch[1]);
          const expiresAt = Date.now() + minutes * 60 * 1000;
          setCooldownExpiresAt(expiresAt);
          setCooldownRemaining(minutes);
        }
      }
    } catch {
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLastUpdated();
    fetchCooldownStatus();
  }, [fetchLastUpdated, fetchCooldownStatus]);

  useEffect(() => {
    if (!cooldownExpiresAt) return;

    const interval = setInterval(() => {
      const remainingMs = Math.max(0, cooldownExpiresAt - Date.now());
      const remainingMinutes = remainingMs / (1000 * 60);

      if (remainingMinutes <= 0) {
        setCooldownRemaining(null);
        setCooldownExpiresAt(null);
      } else {
        setCooldownRemaining(remainingMinutes);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [cooldownExpiresAt]);

  const formatLastUpdated = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <main className="min-h-screen flex flex-col">
      <div className="container mx-auto px-4 flex flex-col flex-1"> 
        <div className="max-w-[736px] mx-auto w-full flex flex-col flex-1">
          <div className="text-center pt-12 mb-4">
            <h1 className="text-2xl font-semibold text-gray-900 mb-1">EmptyClassroom</h1>
            <p className="text-lg text-gray-600">
              Find empty classrooms to study in at <span className="md:hidden">BU</span><span className="hidden md:inline">Boston University</span>
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 mb-4">
            {!lastUpdated ? (
              <span className="text-sm text-gray-500 animate-pulse">Loading data...</span>
            ) : (
              <span className="text-sm text-gray-500">Last updated {formatLastUpdated(lastUpdated)}</span>
            )}
            <RefreshButton
              isRefreshing={isRefreshing}
            isCooldownLoading={isCooldownLoading}
              cooldownRemaining={cooldownRemaining}
              onRefresh={handleRefresh}
            />
          </div>
          <BuildingsContent buildings={buildings} error={buildingsError} />
          <footer className="mt-auto py-4 flex justify-center gap-6 bg-white/80 backdrop-blur-sm -mx-4 px-4">
            <NotesTooltip>
              <span className="text-gray-500 hover:text-gray-700 cursor-pointer">
                Notes
              </span>
            </NotesTooltip>
            <a
              href="https://form.typeform.com/to/t17kzOqs"
              target="_blank"
              className="text-gray-500 hover:text-gray-700 cursor-pointer"
            >
              Request
            </a>
            <a 
              href="https://github.com/justin9668/EmptyClassroom" 
              target="_blank" 
              className="text-gray-500 hover:text-gray-700 cursor-pointer"
            >
              GitHub
            </a>
          </footer>
        </div>
      </div>
    </main>
  );
}