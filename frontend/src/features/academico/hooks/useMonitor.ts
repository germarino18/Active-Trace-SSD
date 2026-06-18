import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import * as monitorService from '../services/monitor.service';
import type { MonitorFilters } from '../services/monitor.service';
import type { MonitorResponse } from '../types';

const defaultFilters: MonitorFilters = {};

export function useMonitor(materiaId: string) {
  const [filters, setFilters] = useState<MonitorFilters>(defaultFilters);
  const [activeFilters, setActiveFilters] = useState<MonitorFilters>(defaultFilters);

  const query = useQuery<MonitorResponse>({
    queryKey: ['monitor', materiaId, activeFilters],
    queryFn: () => monitorService.getMonitorData(materiaId, activeFilters),
    enabled: !!materiaId,
  });

  const applyFilters = useCallback(() => {
    setActiveFilters({ ...filters });
  }, [filters]);

  const clearFilters = useCallback(() => {
    setFilters(defaultFilters);
    setActiveFilters(defaultFilters);
  }, []);

  const updateFilter = useCallback(<K extends keyof MonitorFilters>(key: K, value: MonitorFilters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  return {
    filters,
    updateFilter,
    applyFilters,
    clearFilters,
    query,
  };
}
