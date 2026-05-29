import { z } from "zod";

export const bookmarkFormSchema = z.object({
  url: z
    .string()
    .trim()
    .min(1, { message: "URL is required" })
    .url({ message: "Please enter a valid URL (including http/https)" }),
  title: z.string().trim().optional().or(z.literal("")),
  notes: z.string().trim().optional().or(z.literal("")),
  tags: z.array(z.string()), // UUID strings
});

export type BookmarkFormData = z.infer<typeof bookmarkFormSchema>;

export const tagFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, { message: "Tag name is required" })
    .max(50, { message: "Tag name must be under 50 characters" }),
});

export type TagFormData = z.infer<typeof tagFormSchema>;
