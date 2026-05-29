import { toast } from "sonner";
import type { FieldValues } from "react-hook-form";

/**
 * Displays a success toast message.
 */
export const ToastSuccess = (message: string, options?: Parameters<typeof toast.success>[1]) => {
  toast.success(message, options);
};

/**
 * Displays an error toast message.
 */
export const ToastFail = (message: string, options?: Parameters<typeof toast.error>[1]) => {
  toast.error(message, options);
};

/**
 * Displays a warning toast message.
 */
export const ToastWarn = (message: string) => {
  toast.warning(message);
};

/**
 * Removes keys with empty strings, null, or undefined values from an object.
 */
export const cleanObject = <T extends Record<string, unknown>>(obj: T): T => {
  const result = {} as T;
  (Object.keys(obj) as Array<keyof T>).forEach((key) => {
    const value = obj[key];
    if (value !== "" && value !== null && value !== undefined) {
      result[key] = value;
    }
  });
  return result;
};

/**
 * Recursively extracts only the dirty (modified) values from a form.
 */
export const getDirtyValues = <T extends FieldValues>(
  dirtyFields: Partial<Readonly<Record<keyof T, boolean | object>>>,
  allValues: T
): Partial<T> => {
  if (!dirtyFields || Object.keys(dirtyFields).length === 0) {
    return {} as Partial<T>;
  }

  return Object.keys(dirtyFields).reduce((acc, key) => {
    const dirtyValue = dirtyFields[key as keyof T];
    const value = allValues[key as keyof T];

    if (dirtyValue === true) {
      acc[key as keyof T] = value;
    } else if (typeof dirtyValue === "object" && dirtyValue !== null) {
      if (Array.isArray(value)) {
        acc[key as keyof T] = value;
      } else if (typeof value === "object" && value !== null) {
        acc[key as keyof T] = getDirtyValues(
          dirtyValue as Partial<Readonly<Record<string, boolean | object>>>,
          value as FieldValues
        ) as T[keyof T];
      }
    }

    return acc;
  }, {} as Partial<T>);
};
