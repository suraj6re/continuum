export default function Card({ children, className = '', title, action }) {
  return (
    <div className={`bg-bg-card rounded-xl shadow-sm border border-border-warm p-6 ${className}`}>
      {title && (
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}
