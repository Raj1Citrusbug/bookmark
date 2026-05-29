import React from "react";
import { Trash2, AlertTriangle, HelpCircle, X } from "lucide-react";
import { Button } from "@/components/atoms";
import { cn } from "@/lib/utils";

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean;
  variant?: "primary" | "destructive" | "warning";
  icon?: React.ReactNode;
}

const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  isLoading = false,
  variant = "primary",
  icon,
}: ConfirmationModalProps) => {
  if (!isOpen) return null;

  const defaultIcon = () => {
    switch (variant) {
      case "destructive":
        return <Trash2 size={20} />;
      case "warning":
        return <AlertTriangle size={20} />;
      default:
        return <HelpCircle size={20} />;
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-eerie-black/60 backdrop-blur-sm z-50 animate-in fade-in duration-200">
      {/* Modal Card */}
      <div className="w-full max-w-md bg-card text-card-foreground p-6 rounded-xl shadow-2xl border border-border animate-in zoom-in-95 duration-200 relative">
        {/* Close button in top-right corner to match system forms */}
        <button
          type="button"
          onClick={onClose}
          disabled={isLoading}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-muted transition-all"
        >
          <X size={18} />
        </button>

        <div className="flex items-start gap-4 pr-6">
          {/* Variant Icon */}
          <div
            className={cn(
              "flex h-11 w-11 shrink-0 items-center justify-center rounded-full shadow-sm",
              variant === "destructive" && "bg-destructive/10 text-destructive",
              variant === "warning" && "bg-gold-yellow/10 text-gold-yellow",
              variant === "primary" && "bg-muted text-foreground"
            )}
          >
            {icon || defaultIcon()}
          </div>

          {/* Title and message */}
          <div className="flex-1 space-y-1.5">
            <h3 className="text-lg font-display font-extrabold text-foreground leading-snug">
              {title}
            </h3>
            <p className="text-sm font-sans text-muted-foreground leading-relaxed">
              {description}
            </p>
          </div>
        </div>

        {/* Action Panel */}
        <div className="flex justify-end gap-3 pt-4 border-t border-border/60 mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
            className="h-10 px-4 py-2 border-border/80 text-foreground hover:bg-muted font-semibold"
          >
            {cancelText}
          </Button>
          <Button
            type="button"
            variant={variant === "destructive" ? "destructive" : "default"}
            disabled={isLoading}
            onClick={onConfirm}
            className={cn(
              "h-10 px-4 py-2 font-semibold shadow-sm",
              variant === "warning" && "bg-gold-yellow hover:bg-gold-yellow/90 text-eerie-black"
            )}
          >
            {isLoading ? "Processing..." : confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
};

export { ConfirmationModal };
export type { ConfirmationModalProps };

