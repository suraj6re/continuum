import Button from '../components/Button';

export default function Login({ onLogin }) {
  return (
    <div className="min-h-screen bg-bg-page flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">StructIQ</h1>
          <p className="text-text-secondary">Construction Intelligence Platform</p>
        </div>

        <div className="bg-bg-card rounded-xl shadow-lg border border-border-warm p-8">
          <h2 className="text-2xl font-bold text-brand-charcoal mb-6">Sign In</h2>
          
          <form onSubmit={(e) => { e.preventDefault(); onLogin(); }} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Email</label>
              <input 
                type="email" 
                placeholder="your.email@company.com"
                className="w-full px-4 py-3 border border-border-warm rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Password</label>
              <input 
                type="password" 
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-border-warm rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
              />
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                <span className="text-text-secondary">Remember me</span>
              </label>
              <button type="button" className="text-brand-orange hover:underline">Forgot password?</button>
            </div>

            <Button type="submit" className="w-full">Sign In</Button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-6">
            Don't have an account? <button type="button" className="text-brand-orange hover:underline">Sign up</button>
          </p>
        </div>
      </div>
    </div>
  );
}
