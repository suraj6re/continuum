export default function Stepper({ steps, currentStep }) {
  return (
    <div className="flex items-center justify-between">
      {steps.map((step, idx) => (
        <div key={idx} className="flex items-center flex-1">
          <div className="flex flex-col items-center">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm
              ${idx < currentStep ? 'bg-emerald-600 text-white' : 
                idx === currentStep ? 'bg-brand-orange text-white' : 
                'bg-bg-section text-text-muted border-2 border-border-warm'}`}>
              {idx < currentStep ? '✓' : idx + 1}
            </div>
            <span className={`mt-2 text-xs font-medium ${idx === currentStep ? 'text-brand-orange' : 'text-text-secondary'}`}>
              {step}
            </span>
          </div>
          {idx < steps.length - 1 && (
            <div className={`flex-1 h-0.5 mx-2 ${idx < currentStep ? 'bg-emerald-600' : 'bg-border-warm'}`} />
          )}
        </div>
      ))}
    </div>
  );
}
