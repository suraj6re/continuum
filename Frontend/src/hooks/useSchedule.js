import { useState, useEffect, useMemo } from 'react';
import { generateSchedule, findCriticalPath } from '../services/scheduleGenerator';

export const useSchedule = (qtoElements, processingStatus) => {
  const [customProductivity, setCustomProductivity] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (processingStatus === 'complete' && qtoElements.length > 0) {
      setLoading(true);
      setTimeout(() => setLoading(false), 500);
    }
  }, [processingStatus, qtoElements]);

  const scheduleData = useMemo(() => {
    if (processingStatus !== 'complete' || !qtoElements || qtoElements.length === 0) {
      return { tasks: [], summary: { total_tasks: 0, total_duration: 0, structural_duration: 0, finishing_duration: 0 } };
    }
    return generateSchedule(qtoElements, customProductivity);
  }, [qtoElements, customProductivity, processingStatus]);

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
