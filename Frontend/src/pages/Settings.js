import Card from '../components/Card';
import Button from '../components/Button';

export default function Settings() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Settings</h1>
        <p className="text-text-secondary">Manage your account and preferences</p>
      </div>

      <div className="space-y-6">
        <Card title="Profile Information">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Full Name</label>
              <input type="text" defaultValue="John Doe" className="w-full px-4 py-2 border border-border-warm rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Email</label>
              <input type="email" defaultValue="john.doe@company.com" className="w-full px-4 py-2 border border-border-warm rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Role</label>
              <input type="text" defaultValue="Civil Engineer" className="w-full px-4 py-2 border border-border-warm rounded-lg" />
            </div>
            <Button>Save Changes</Button>
          </div>
        </Card>

        <Card title="Preferences">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-brand-charcoal">Email Notifications</p>
                <p className="text-sm text-text-secondary">Receive updates about your projects</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-brand-charcoal">Auto-save Reports</p>
                <p className="text-sm text-text-secondary">Automatically save generated reports</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5" />
            </div>
          </div>
        </Card>

        <Card title="API Access">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">API Key</label>
              <div className="flex space-x-2">
                <input type="password" value="sk_live_••••••••••••••••" className="flex-1 px-4 py-2 border border-border-warm rounded-lg" readOnly />
                <Button variant="outline">Regenerate</Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
