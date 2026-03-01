import { useState, useEffect, useMemo } from 'react';
import { generateSchedule, findCriticalPath } from '../services/scheduleGenerator';
import { fetchScheduleData } from '../services/scheduleService';
import { useProjectStore } from './useProjectStore';

export const useSchedule = (qtoElements, processingStatus) => {
  const { currentProjectId } = useProjectStore();
  const [customProductivity, setCustomProductivity] = useState({});
  const [loading, setLoading] = useState(false);
  const [backendSchedule, setBackendSchedule] = useState(null);

  useEffect(() => {
    if (processingStatus === 'complete' && currentProjectId) {
      setLoading(true);
      fetchScheduleData(currentProjectId)
        .then(data => {
          if (data) setBackendSchedule(data);
        })
        .catch(err => console.error('Schedule fetch error:', err))
        .finally(() => setLoading(false));
    }
  }, [processingStatus, currentProjectId]);

  const scheduleData = useMemo(() => {
    if (processingStatus !== 'complete') {
      return { tasks: [], summary: { total_tasks: 0, total_duration: 0, structural_duration: 0, finishing_duration: 0 } };
    }
    if (backendSchedule) return backendSchedule;
    if (qtoElements && qtoElements.length > 0) {
      return generateSchedule(qtoElements, customProductivity);
    }
    return { tasks: [], summary: { total_tasks: 0, total_duration: 0, structural_duration: 0, finishing_duration: 0 } };
  }, [qtoElements, customProductivity, processingStatus, backendSchedule]);

  const criticalPath = useMemo(() => {
    if (scheduleData.tasks.length === 0) return new Set();
    return findCriticalPath(scheduleData.tasks);
  }, [scheduleData.tasks]);

  const updateProductivity = (newRates) => {
    setCustomProductivity(newRates);
  };

  return {
    tasks: scheduleData.tasks,
    summary: scheduleData.summary,
    criticalPath,
    loading,
    updateProductivity
  };
};
