const DEFAULT_PRODUCTIVITY = {
  'Concrete Slab': 50,
  'Concrete': 50,
  'Column Concrete': 45,
  'Beam Concrete': 45,
  'Steel Reinforcement': 1500,
  'Brick Masonry': 100,
  'Masonry': 100,
  'Plaster Work': 150,
  'Plastering': 150,
  'Floor Tiles': 120,
  'Tiles': 120,
  'Painting': 200,
  'Formwork': 80,
  'Excavation': 100
};

const CATEGORY_ORDER = {
  'Foundation': 1,
  'Structural': 2,
  'Walls': 3,
  'Finishing': 4
};

const getElementCategory = (elementName) => {
  const name = elementName.toLowerCase();
  if (name.includes('excavation') || name.includes('foundation')) return 'Foundation';
  if (name.includes('concrete') || name.includes('steel') || name.includes('column') || name.includes('beam') || name.includes('slab') || name.includes('formwork')) return 'Structural';
  if (name.includes('brick') || name.includes('masonry') || name.includes('wall')) return 'Walls';
  return 'Finishing';
};

const getProductivityRate = (elementName, customRates = {}) => {
  for (const [key, rate] of Object.entries(customRates)) {
    if (elementName.toLowerCase().includes(key.toLowerCase())) {
      return rate;
    }
  }
  for (const [key, rate] of Object.entries(DEFAULT_PRODUCTIVITY)) {
    if (elementName.toLowerCase().includes(key.toLowerCase())) {
      return rate;
    }
  }
  return 100;
};

const generateTasksForElement = (element, taskIdCounter, customProductivity) => {
  const category = getElementCategory(element.element_name || element.name);
  const tasks = [];
  
  const quantity = element.quantity || 0;
  const productivity = getProductivityRate(element.element_name || element.name, customProductivity);
  const baseDuration = Math.ceil(quantity / productivity);

  if (category === 'Structural' && (element.element_name || element.name).toLowerCase().includes('concrete')) {
    tasks.push({
      id: `T${taskIdCounter++}`,
      name: `Formwork - ${element.element_name || element.name}`,
      element_name: element.element_name || element.name,
      quantity,
      productivity: productivity * 1.5,
      duration_days: Math.ceil(baseDuration * 0.4),
      category,
      dependencies: []
    });
    
    tasks.push({
      id: `T${taskIdCounter++}`,
      name: `Reinforcement - ${element.element_name || element.name}`,
      element_name: element.element_name || element.name,
      quantity,
      productivity,
      duration_days: Math.ceil(baseDuration * 0.3),
      category,
      dependencies: [tasks[0].id]
    });
    
    tasks.push({
      id: `T${taskIdCounter++}`,
      name: `Pouring - ${element.element_name || element.name}`,
      element_name: element.element_name || element.name,
      quantity,
      productivity,
      duration_days: Math.ceil(baseDuration * 0.2),
      category,
      dependencies: [tasks[1].id]
    });
    
    tasks.push({
      id: `T${taskIdCounter++}`,
      name: `Curing - ${element.element_name || element.name}`,
      element_name: element.element_name || element.name,
      quantity,
      productivity,
      duration_days: 7,
      category,
      dependencies: [tasks[2].id]
    });
  } else {
    tasks.push({
      id: `T${taskIdCounter++}`,
      name: element.element_name || element.name,
      element_name: element.element_name || element.name,
      quantity,
      productivity,
      duration_days: baseDuration || 1,
      category,
      dependencies: []
    });
  }

  return tasks;
};

const calculateSchedule = (tasks) => {
  const taskMap = {};
  tasks.forEach(task => {
    taskMap[task.id] = { ...task, start_day: 0, end_day: 0 };
  });

  const calculateStartDay = (taskId, visited = new Set()) => {
    if (visited.has(taskId)) return 0;
    visited.add(taskId);

    const task = taskMap[taskId];
    if (!task.dependencies || task.dependencies.length === 0) {
      task.start_day = 0;
    } else {
      let maxEndDay = 0;
      task.dependencies.forEach(depId => {
        const depTask = taskMap[depId];
        if (depTask) {
          if (depTask.end_day === 0) {
            calculateStartDay(depId, visited);
          }
          maxEndDay = Math.max(maxEndDay, depTask.end_day);
        }
      });
      task.start_day = maxEndDay;
    }
    task.end_day = task.start_day + task.duration_days;
  };

  tasks.forEach(task => calculateStartDay(task.id));

  return Object.values(taskMap);
};

const addCategoryDependencies = (allTasks) => {
  const tasksByCategory = {};
  
  allTasks.forEach(task => {
    if (!tasksByCategory[task.category]) {
      tasksByCategory[task.category] = [];
    }
    tasksByCategory[task.category].push(task);
  });

  const categories = Object.keys(tasksByCategory).sort((a, b) => 
    (CATEGORY_ORDER[a] || 99) - (CATEGORY_ORDER[b] || 99)
  );

  for (let i = 1; i < categories.length; i++) {
    const prevCategory = categories[i - 1];
    const currentCategory = categories[i];
    
    const prevTasks = tasksByCategory[prevCategory];
    const currentTasks = tasksByCategory[currentCategory];
    
    if (prevTasks.length > 0 && currentTasks.length > 0) {
      const lastPrevTask = prevTasks[prevTasks.length - 1];
      currentTasks[0].dependencies.push(lastPrevTask.id);
    }
  }

  return allTasks;
};

export const generateSchedule = (qtoElements, customProductivity = {}) => {
  if (!qtoElements || qtoElements.length === 0) {
    return { tasks: [], summary: { total_tasks: 0, total_duration: 0, structural_duration: 0, finishing_duration: 0 } };
  }

  let taskIdCounter = 1;
  let allTasks = [];

  const sortedElements = [...qtoElements].sort((a, b) => {
    const catA = getElementCategory(a.element_name || a.name);
    const catB = getElementCategory(b.element_name || b.name);
    return (CATEGORY_ORDER[catA] || 99) - (CATEGORY_ORDER[catB] || 99);
  });

  sortedElements.forEach(element => {
    const tasks = generateTasksForElement(element, taskIdCounter, customProductivity);
    allTasks = allTasks.concat(tasks);
    taskIdCounter += tasks.length;
  });

  allTasks = addCategoryDependencies(allTasks);
  const scheduledTasks = calculateSchedule(allTasks);

  const totalDuration = Math.max(...scheduledTasks.map(t => t.end_day), 0);
  const structuralDuration = scheduledTasks
    .filter(t => t.category === 'Structural')
    .reduce((max, t) => Math.max(max, t.end_day), 0);
  const finishingDuration = scheduledTasks
    .filter(t => t.category === 'Finishing')
    .reduce((sum, t) => sum + t.duration_days, 0);

  return {
    tasks: scheduledTasks,
    summary: {
      total_tasks: scheduledTasks.length,
      total_duration: totalDuration,
      structural_duration: structuralDuration,
      finishing_duration: finishingDuration
    }
  };
};

export const findCriticalPath = (tasks) => {
  const criticalTaskIds = new Set();
  const maxEndDay = Math.max(...tasks.map(t => t.end_day), 0);
  
  const criticalTasks = tasks.filter(t => t.end_day === maxEndDay);
  
  const tracePath = (task) => {
    criticalTaskIds.add(task.id);
    if (task.dependencies && task.dependencies.length > 0) {
      task.dependencies.forEach(depId => {
        const depTask = tasks.find(t => t.id === depId);
        if (depTask) {
          tracePath(depTask);
        }
      });
    }
  };

  criticalTasks.forEach(tracePath);
  
  return criticalTaskIds;
};

export const exportScheduleToCSV = (tasks, summary, productivity) => {
  const headers = ['Task ID', 'Task Name', 'Category', 'Quantity', 'Productivity', 'Duration (days)', 'Start Day', 'End Day', 'Dependencies'];
  const rows = tasks.map(task => [
    task.id,
    task.name,
    task.category,
    task.quantity,
    task.productivity,
    task.duration_days,
    task.start_day,
    task.end_day,
    task.dependencies.join(';')
  ]);

  const summaryRows = [
    [],
    ['Summary'],
    ['Total Tasks', summary.total_tasks],
    ['Total Duration', summary.total_duration + ' days'],
    ['Structural Duration', summary.structural_duration + ' days'],
    ['Finishing Duration', summary.finishing_duration + ' days']
  ];

  const csv = [headers, ...rows, ...summaryRows]
    .map(row => row.join(','))
    .join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `schedule-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

export const exportScheduleToJSON = (tasks, summary, productivity) => {
  const data = {
    summary,
    tasks,
    productivity_rates: productivity,
    exported_at: new Date().toISOString()
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `schedule-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};
