import Button from '../components/Button';

export default function Landing({ onGetStarted }) {
  const features = [
    { title: 'Automated QTO', desc: 'AI-powered quantity take-off from 2D drawings'},
    { title: 'Cost Intelligence', desc: 'Smart cost estimation with uncertainty bands'},
    { title: 'Smart Scheduling', desc: 'Phase-wise schedules with productivity logic'},
    { title: 'Validation Engine', desc: 'Confidence scoring and precision checks'},
  ];

  return (
    <div className="min-h-screen bg-bg-page">
      <nav className="bg-bg-card border-b border-border-warm">
        <div className="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-brand-charcoal">StructIQ</h1>
            <p className="text-xs text-text-secondary">AI-Powered Construction Intelligence</p>
          </div>
          <div className="space-x-4">
            <Button variant="outline" size="sm" onClick={onGetStarted}>Login</Button>
            <Button size="sm" onClick={onGetStarted}>Sign Up</Button>
          </div>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-8 py-20 text-center">
        <h2 className="text-5xl font-bold text-brand-charcoal mb-6">
          Transform Construction Workflows with AI
        </h2>
        <p className="text-xl text-text-secondary mb-8 max-w-3xl mx-auto">
          End-to-end construction intelligence platform that reads drawings, extracts quantities, 
          validates data, estimates costs, and generates schedules—all powered by AI.
        </p>
        <div className="flex justify-center space-x-4">
          <Button size="lg" onClick={onGetStarted}>Upload Drawing</Button>
          <Button variant="outline" size="lg">Request Demo</Button>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, idx) => (
            <div key={idx} className="bg-bg-card rounded-xl p-6 border border-border-warm hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-brand-charcoal mb-2">{feature.title}</h3>
              <p className="text-sm text-text-secondary">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-8 py-16">
        <h3 className="text-3xl font-bold text-center text-brand-charcoal mb-12">System Workflow</h3>
        <div className="bg-bg-card rounded-xl p-8 border border-border-warm">
          <div className="flex flex-wrap justify-center items-center gap-4">
            {['Upload', 'Extract', 'QTO', 'Validate', 'Cost', 'Schedule', 'Report'].map((step, idx) => (
              <div key={idx} className="flex items-center">
                <div className="bg-brand-orange text-white px-6 py-3 rounded-lg font-medium">
                  {step}
                </div>
                {idx < 6 && <span className="mx-2 text-brand-amber text-2xl">→</span>}
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="bg-brand-charcoal text-white py-8 mt-20">
        <div className="max-w-7xl mx-auto px-8 text-center">
          <p className="text-sm">© 2024 StructIQ. Enterprise Construction Intelligence Platform.</p>
        </div>
      </footer>
    </div>
  );
}
