export default function Button({ children, variant = 'primary', size = 'md', className = '', ...props }) {
  const baseStyles = 'font-medium rounded-xl transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-brand-orange text-white hover:bg-[#C2410C]',
    secondary: 'bg-brand-amber text-white hover:bg-[#B45309]',
    outline: 'border-2 border-brand-orange text-brand-orange hover:bg-brand-orange hover:text-white',
  };
  
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };
  
  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
