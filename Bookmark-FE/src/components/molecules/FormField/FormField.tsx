import { useState } from "react";
import { useController } from "react-hook-form";
import type { Control, FieldPath, FieldValues } from "react-hook-form";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface FormFieldProps<T extends FieldValues> {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  placeholder?: string;
  type?: "text" | "email" | "password" | "number" | "textarea";
  className?: string;
  inputClassName?: string;
  labelClassName?: string;
  disabled?: boolean;
}

function FormField<T extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  type = "text",
  className,
  inputClassName,
  labelClassName,
  disabled,
}: FormFieldProps<T>) {
  const {
    field,
    fieldState: { error },
  } = useController({ name, control });

  const [showPassword, setShowPassword] = useState(false);

  const isPassword = type === "password";
  const inputType = isPassword ? (showPassword ? "text" : "password") : type;

  return (
    <div className={cn("flex flex-col gap-1.5 w-full", className)}>
      <label
        htmlFor={name}
        className={cn(
          "text-xs font-semibold uppercase tracking-wider text-muted-foreground",
          labelClassName
        )}
      >
        {label}
      </label>
      
      <div className="relative w-full">
        {type === "textarea" ? (
          <textarea
            id={name}
            placeholder={placeholder}
            disabled={disabled}
            className={cn(
              "flex min-h-[100px] w-full rounded-lg border border-input bg-card px-3 py-2 text-sm shadow-sm transition-all placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary disabled:cursor-not-allowed disabled:opacity-50 resize-y",
              error && "border-destructive focus:ring-destructive focus:border-destructive",
              inputClassName
            )}
            {...field}
            value={field.value ?? ""}
          />
        ) : (
          <div className="relative flex items-center">
            <input
              id={name}
              type={inputType}
              placeholder={placeholder}
              disabled={disabled}
              className={cn(
                "flex h-11 w-full rounded-lg border border-input bg-card px-3 py-2 text-sm shadow-sm transition-all placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary disabled:cursor-not-allowed disabled:opacity-50",
                error && "border-destructive focus:ring-destructive focus:border-destructive",
                isPassword && "pr-10",
                inputClassName
              )}
              {...field}
              value={field.value ?? ""}
            />
            {isPassword && (
              <button
                type="button"
                disabled={disabled}
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground focus:outline-none"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            )}
          </div>
        )}
      </div>

      {error && (
        <span className="text-xs font-medium text-destructive transition-all duration-200">
          {error.message}
        </span>
      )}
    </div>
  );
}

export { FormField };
export type { FormFieldProps };
