import { OPTIMIZATION_MODES } from '../services/optimizationEngine';

export default function OptimizationControls({ mode, setMode, variables, updateVariable, onReset, onSave }) {
  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">Optimization Mode</label>
        <div className="space-y-2">
          <button
            onClick={() => setMode(OPTIMIZATION_MODES.MINIMIZE_DURATION)}
            className={`w-full px-4 py-2 text-sm rounded-lg border ${
              mode === OPTIMIZATION_MODES.MINIMIZE_DURATION
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            Minimize Duration
          </button>
          <button
            onClick={() => setMode(OPTIMIZATION_MODES.MINIMIZE_COST)}
            className={`w-full px-4 py-2 text-sm rounded-lg border ${
              mode === OPTIMIZATION_MODES.MINIMIZE_COST
                ? 'bg-green-600 text-white border-green-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            Minimize Cost
          </button>
          <button
            onClick={() => setMode(OPTIMIZATION_MODES.BALANCED)}
            className={`w-full px-4 py-2 text-sm rounded-lg border ${
              mode === OPTIMIZATION_MODES.BALANCED
                ? 'bg-purple-600 text-white border-purple-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            Balanced
          </button>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Productivity Multiplier: {variables.productivityMultiplier.toFixed(2)}x
        </label>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={variables.productivityMultiplier}
          onChange={(e) => updateVariable('productivityMultiplier', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0.5x</span>
          <span>2.0x</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Overtime Multiplier: {variables.overtimeMultiplier.toFixed(2)}x
        </label>
        <input
          type="range"
          min="1.0"
          max="1.5"
          step="0.05"
          value={variables.overtimeMultiplier}
          onChange={(e) => updateVariable('overtimeMultiplier', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>1.0x</span>
          <span>1.5x</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Crew Size Multiplier: {variables.crewMultiplier.toFixed(2)}x
        </label>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={variables.crewMultiplier}
          onChange={(e) => updateVariable('crewMultiplier', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0.5x</span>
          <span>2.0x</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Price Volatility: {((variables.priceVolatility - 1) * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          min="0.8"
          max="1.3"
          step="0.05"
          value={variables.priceVolatility}
          onChange={(e) => updateVariable('priceVolatility', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>-20%</span>
          <span>+30%</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Resource Level</label>
        <select
          value={variables.resourceLevel}
          onChange={(e) => updateVariable('resourceLevel', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="pt-4 border-t border-gray-200 space-y-2">
        <button
          onClick={onSave}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          Save Scenario
        </button>
        <button
          onClick={onReset}
          className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium"
        >
          Reset to Baseline
        </button>
      </div>
    </div>
  );
}
