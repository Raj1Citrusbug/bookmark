import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { bookmarkFormSchema, type BookmarkFormData } from "@/constants/schemas/bookmark";
import { createBookmark, updateBookmark, getTags } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { ToastSuccess } from "@/utils/helpers";
import { Button } from "@/components/atoms";
import { FormField } from "@/components/molecules";
import type { Bookmark } from "@/types/bookmark";
import type { Tag } from "@/types/tag";
import { X, Plus } from "lucide-react";
import { TagCreateModal } from "../TagCreateModal";

interface BookmarkFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialData?: Bookmark | null;
  onOpenTagModal?: () => void;
}

const BookmarkFormModal = ({
  isOpen,
  onClose,
  onSuccess,
  initialData,
}: BookmarkFormModalProps) => {
  const { call } = useApiCall();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);

  const isEdit = !!initialData;

  const { control, handleSubmit, reset, setValue, watch } = useForm<BookmarkFormData>({
    resolver: zodResolver(bookmarkFormSchema),
    defaultValues: {
      url: "",
      title: "",
      notes: "",
      tags: [],
    },
  });

  // Fetch tags
  const loadTags = () => {
    call(
      () => getTags(),
      (response) => {
        setAvailableTags(response.data.data || []);
      }
    );
  };

  useEffect(() => {
    if (isOpen) {
      loadTags();
      if (initialData) {
        setValue("url", initialData.url);
        setValue("title", initialData.title || "");
        setValue("notes", initialData.notes || "");
        setValue("tags", (initialData.tags || []).map((t) => t.id));
      } else {
        reset({
          url: "",
          title: "",
          notes: "",
          tags: [],
        });
      }
    }
  }, [isOpen, initialData]);

  const selectedTags = watch("tags") || [];

  const handleTagToggle = (tagId: string) => {
    if (selectedTags.includes(tagId)) {
      setValue("tags", selectedTags.filter((id) => id !== tagId));
    } else {
      setValue("tags", [...selectedTags, tagId]);
    }
  };

  const onSubmit = (data: BookmarkFormData) => {
    setIsSubmitting(true);
    
    // Clean payload
    const payload = {
      url: data.url,
      title: data.title || null,
      notes: data.notes || null,
      tags: data.tags && data.tags.length > 0 ? data.tags : [],
    };

    if (isEdit && initialData) {
      call(
        () => updateBookmark(initialData.id, {
          title: payload.title,
          notes: payload.notes,
          tags: payload.tags,
        }),
        () => {
          ToastSuccess("Bookmark updated successfully!");
          onSuccess();
          onClose();
        },
        undefined,
        () => setIsSubmitting(false)
      );
    } else {
      call(
        () => createBookmark(payload),
        () => {
          ToastSuccess("Bookmark saved successfully!");
          onSuccess();
          onClose();
        },
        undefined,
        () => setIsSubmitting(false)
      );
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-eerie-black/60 backdrop-blur-sm z-40 animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-card text-card-foreground p-6 rounded-xl shadow-2xl border border-border animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between mb-4 border-b border-border pb-3">
          <h3 className="text-lg font-display font-bold">
            {isEdit ? "Edit Bookmark" : "Add New Bookmark"}
          </h3>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-muted"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={control}
            name="url"
            label="Bookmark URL"
            placeholder="e.g. https://github.com/fastapi/fastapi"
            disabled={isSubmitting || isEdit} // URL shouldn't be editable directly to keep consistency
          />

          <FormField
            control={control}
            name="title"
            label="Title (Optional)"
            placeholder="e.g. FastAPI GitHub Repository (Leaves blank to auto-fetch)"
            disabled={isSubmitting}
          />

          <FormField
            control={control}
            name="notes"
            label="Notes (Optional)"
            type="textarea"
            placeholder="Add brief description or reminders..."
            disabled={isSubmitting}
          />

          {/* Tags Multi-select */}
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Tags
              </span>
              <button
                type="button"
                onClick={() => setIsTagModalOpen(true)}
                className="flex items-center gap-1 text-xs font-bold text-primary hover:text-primary/80"
              >
                <Plus size={14} /> New Tag
              </button>
            </div>

            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 border border-border rounded-lg bg-muted/40">
              {availableTags.length === 0 ? (
                <span className="text-xs text-muted-foreground italic py-1">No tags available. Create one first!</span>
              ) : (
                availableTags.map((tag) => {
                  const isSelected = selectedTags.includes(tag.id);
                  return (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => handleTagToggle(tag.id)}
                      className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                        isSelected
                          ? "bg-primary border-primary text-primary-foreground"
                          : "bg-card border-input hover:bg-muted text-foreground"
                      }`}
                    >
                      {tag.name}
                    </button>
                  );
                })
              )}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-border mt-6">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-gold-yellow text-eerie-black font-semibold hover:bg-gold-yellow/90"
            >
              {isSubmitting ? "Saving..." : isEdit ? "Update" : "Save Bookmark"}
            </Button>
          </div>
        </form>
      </div>

      {/* Internal Tag Creation Dialog */}
      <TagCreateModal
        isOpen={isTagModalOpen}
        onClose={() => setIsTagModalOpen(false)}
        onSuccess={() => {
          loadTags();
          onSuccess(); // Triggers parent refresh (like reloading the tag cloud)
        }}
      />
    </div>
  );
};

export { BookmarkFormModal };
export type { BookmarkFormModalProps };
