import { createPortal } from "react-dom";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingProps {
  className?: string;
  size?: number;
  variant?: "page" | "overlay" | "spinner";
  text?: string;
  blur?: boolean;
}

const Loading = ({ 
  className, 
  size = 32, 
  variant = "spinner", 
  text, 
  blur = true 
}: LoadingProps) => {
  const spinner = (
    <div className="relative flex items-center justify-center">
      <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-ping" style={{ width: size, height: size }} />
      <Loader2 
        className="animate-spin text-primary" 
        size={size} 
        strokeWidth={2.5}
      />
    </div>
  );

  const content = (
    <div 
      className={cn(
        "fixed inset-0 z-[100] flex flex-col items-center justify-center gap-4",
        blur && "backdrop-blur-[2px] bg-background/30",
        !blur && "bg-background/50",
        variant === "overlay" && "absolute",
        className
      )}
    >
      <div className="flex flex-col items-center gap-4">
        {spinner}
        {text && (
          <p className="font-sans text-sm font-medium text-foreground/80 tracking-wide animate-pulse">
            {text}
          </p>
        )}
      </div>
    </div>
  );

  if (variant === "page") {
    return createPortal(content, document.body);
  }

  if (variant === "overlay") {
    return content;
  }

  return (
    <div className={cn("flex items-center justify-center gap-2", className)}>
      {spinner}
      {text && <span className="text-sm font-medium text-muted-foreground">{text}</span>}
    </div>
  );
};

export { Loading };
