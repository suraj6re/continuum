export default function Stepper({ steps, currentStep, onStepClick, activeStep }) {
  // Map display step names to internal step names
  const stepMapping = {
    'Upload': 'upload',
    'Hybrid Normalization': 'normalize',
    'Legend Intelligence': 'extract',
    'Element Extraction': 'parse',
    'Element Graph Model': 'validate'
  };

  return (
    <div className="flex items-start justify-between overflow-x-auto">
      {steps.map((step, idx) => (
        <div key={idx} className="flex items-start flex-shrink-0">
          <div className="flex flex-col items-center">
            <div 
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all
              ${activeStep === step.toLowerCase() ? 'bg-brand-orange text-white ring-2 ring-brand-orange ring-offset-2' :
                idx < currentStep ? 'bg-emerald-600 text-white' : 
                idx === currentStep ? 'bg-brand-orange text-white' : 
                'bg-bg-section text-text-muted border-2 border-border-warm'}
              ${(idx <= 6 && idx < currentStep) || (idx === 0 && onStepClick) ? 'cursor-pointer hover:ring-2 hover:ring-brand-orange hover:scale-110' : ''}`}
              onClick={() => {
                const internalStep = stepMapping[step];
                if (internalStep && onStepClick) {
                  onStepClick(internalStep);
                }
              }}
            >
              {idx < currentStep ? '✓' : idx + 1}
            </div>
            <span className={`mt-2 text-xs font-medium text-center w-20 min-h-[32px] leading-tight ${activeStep === step.toLowerCase() ? 'text-brand-orange' : idx === currentStep ? 'text-brand-orange' : 'text-text-secondary'}`}>
              {step}
            </span>
          </div>
          {idx < steps.length - 1 && (
            <div className={`h-0.5 mx-2 min-w-[20px] flex-1 mt-5 ${idx < currentStep ? 'bg-emerald-600' : 'bg-border-warm'}`} />
          )}
        </div>
      ))}
    </div>
  );
}
