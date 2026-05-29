import React from "react";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}

const AuthLayout = ({ children, title, subtitle }: AuthLayoutProps) => {
  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-gradient-to-tr from-eerie-black via-space to-eerie-black p-4 md:p-8">
      {/* Background decoration elements */}
      <div className="absolute top-10 left-10 w-72 h-72 rounded-full bg-gold-yellow/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-gold-yellow/5 blur-[150px] pointer-events-none" />

      {/* Main glass panel content card */}
      <div className="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl z-10 transition-all duration-300 animate-in fade-in zoom-in-95 duration-500">
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gold-yellow flex items-center justify-center mb-4 shadow-lg shadow-gold-yellow/20">
            <span className="text-2xl font-display font-extrabold text-eerie-black">B</span>
          </div>
          <h1 className="text-3xl font-display font-extrabold tracking-tight text-white mb-2">
            {title}
          </h1>
          <p className="text-sm font-sans font-medium text-spanish-gray">
            {subtitle}
          </p>
        </div>

        {children}
      </div>
    </div>
  );
};

export { AuthLayout };
