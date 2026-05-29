import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { tagFormSchema, type TagFormData } from "@/constants/schemas/bookmark";
import { createTag } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { ToastSuccess } from "@/utils/helpers";
import { Button } from "@/components/atoms";
import { FormField } from "@/components/molecules";
import { X } from "lucide-react";

interface TagCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const TagCreateModal = ({ isOpen, onClose, onSuccess }: TagCreateModalProps) => {
  const { call } = useApiCall();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { control, handleSubmit, reset } = useForm<TagFormData>({
    resolver: zodResolver(tagFormSchema),
    defaultValues: {
      name: "",
    },
  });

  const onSubmit = (data: TagFormData) => {
    setIsSubmitting(true);
    call(
      () => createTag({ name: data.name }),
      () => {
        ToastSuccess("Tag created successfully!");
        reset();
        onSuccess();
        onClose();
      },
      undefined,
      () => setIsSubmitting(false)
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-eerie-black/60 backdrop-blur-sm z-50 animate-in fade-in duration-200">
      <div className="w-full max-w-sm bg-card text-card-foreground p-6 rounded-xl shadow-2xl border border-border animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between mb-4 border-b border-border pb-3">
          <h3 className="text-lg font-display font-bold">Create New Tag</h3>
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
            name="name"
            label="Tag Name"
            placeholder="e.g. tech, personal, read-later"
            disabled={isSubmitting}
          />

          <div className="flex justify-end gap-3 pt-2">
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
              {isSubmitting ? "Creating..." : "Create Tag"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export { TagCreateModal };
export type { TagCreateModalProps };
