import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getBookmark, archiveBookmark, deleteBookmark, refetchTitle } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { ToastSuccess } from "@/utils/helpers";
import { DashboardLayout } from "@/components/templates";
import { BookmarkFormModal } from "@/components/organisms";
import { Button, Loading } from "@/components/atoms";
import { ConfirmationModal } from "@/components/molecules";
import type { Bookmark } from "@/types/bookmark";
import { 
  ArrowLeft, 
  Archive, 
  Trash2, 
  Edit3, 
  RefreshCw, 
  ExternalLink, 
  AlertTriangle,
  Calendar,
  Clock,
  Globe
} from "lucide-react";
import { format } from "date-fns";

const BookmarkDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { call } = useApiCall();

  const [bookmark, setBookmark] = useState<Bookmark | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isRefetching, setIsRefetching] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadBookmark = (showLoader = true) => {
    if (!id) return;
    if (showLoader) setIsLoading(true);
    
    call(
      () => getBookmark(id),
      (response) => {
        const item = response.data.data;
        setBookmark({
          id: item.id,
          userId: item.user_id,
          url: item.url,
          title: item.title,
          notes: item.notes,
          isArchived: item.is_archived,
          isBroken: item.is_broken,
          brokenReason: item.broken_reason,
          lastCheckedAt: item.last_checked_at,
          tags: item.tags || [],
          createdAt: item.created_at,
          updatedAt: item.updated_at,
        });
      },
      () => {
        // Redirection on error (e.g. 404)
        navigate("/");
      },
      () => {
        if (showLoader) setIsLoading(false);
      }
    );
  };

  useEffect(() => {
    loadBookmark(true);
  }, [id]);

  const handleArchiveToggle = () => {
    if (!bookmark) return;
    call(
      () => archiveBookmark(bookmark.id),
      () => {
        ToastSuccess(bookmark.isArchived ? "Bookmark restored to active list." : "Bookmark archived successfully.");
        loadBookmark(false);
      }
    );
  };

  const handleRefetchTitle = () => {
    if (!bookmark) return;
    setIsRefetching(true);
    call(
      () => refetchTitle(bookmark.id),
      () => {
        ToastSuccess("Webpage title extraction queued in background.");
        // Poll for update after 3 seconds
        setTimeout(() => {
          loadBookmark(false);
          setIsRefetching(false);
        }, 3000);
      },
      undefined,
      () => {
        // Safe fallback in case call itself finishes
        setTimeout(() => setIsRefetching(false), 3000);
      }
    );
  };

  const handleDelete = () => {
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!bookmark) return;
    setIsDeleting(true);
    call(
      () => deleteBookmark(bookmark.id),
      () => {
        ToastSuccess("Bookmark deleted successfully.");
        navigate("/");
      },
      undefined,
      () => setIsDeleting(false)
    );
  };

  const formatDateString = (dateStr: string | null) => {
    if (!dateStr) return "Never";
    try {
      return format(new Date(dateStr), "PPP 'at' p");
    } catch (e) {
      return "Invalid date";
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[300px]">
          <Loading variant="spinner" text="Loading details..." />
        </div>
      </DashboardLayout>
    );
  }

  if (!bookmark) return null;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Back Link */}
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-spanish-gray hover:text-foreground transition-all"
        >
          <ArrowLeft size={16} /> Back to Bookmarks
        </Link>

        {/* Detail Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Info */}
          <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 md:p-8 space-y-6 shadow-sm">
            {/* Header info */}
            <div className="space-y-2">
              <h1 className="text-2xl md:text-3xl font-display font-extrabold text-foreground break-words leading-tight">
                {bookmark.title || <span className="text-muted-foreground italic font-semibold">Fetching title...</span>}
              </h1>
              
              <a
                href={bookmark.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-sm text-primary font-semibold hover:underline break-all"
              >
                <Globe size={14} className="shrink-0" />
                <span>{bookmark.url}</span>
                <ExternalLink size={12} className="shrink-0" />
              </a>
            </div>

            {/* Tags Badges */}
            {bookmark.tags && bookmark.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-2 border-t border-border/60">
                {bookmark.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="px-3 py-1 rounded bg-muted/65 text-muted-foreground font-semibold text-xs border border-border/40"
                  >
                    #{tag.name}
                  </span>
                ))}
              </div>
            )}

            {/* Notes Section */}
            <div className="pt-4 border-t border-border/60">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Personal Notes
              </h3>
              {bookmark.notes ? (
                <p className="text-sm font-sans text-foreground/80 leading-relaxed whitespace-pre-wrap">
                  {bookmark.notes}
                </p>
              ) : (
                <p className="text-sm text-muted-foreground italic">No notes added to this bookmark.</p>
              )}
            </div>

            {/* Broken Link Warning */}
            {bookmark.isBroken && (
              <div className="flex items-start gap-3 bg-destructive/10 border border-destructive/35 rounded-lg p-4 text-destructive">
                <AlertTriangle size={20} className="shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm">Broken Link Detected</h4>
                  <p className="text-xs mt-1 leading-relaxed opacity-90">
                    The background checker encountered issues validating this URL. 
                    {bookmark.brokenReason && <span> Reason: <strong>{bookmark.brokenReason}</strong></span>}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Metadata & Actions Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Action buttons */}
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                Bookmark Actions
              </h3>

              {/* Edit */}
              <Button
                onClick={() => setIsFormOpen(true)}
                className="w-full flex items-center justify-center gap-2 bg-muted/50 border border-border hover:bg-muted text-foreground"
              >
                <Edit3 size={16} /> Edit Details
              </Button>

              {/* Refetch Title */}
              <Button
                onClick={handleRefetchTitle}
                disabled={isRefetching}
                className="w-full flex items-center justify-center gap-2 bg-muted/50 border border-border hover:bg-muted text-foreground"
              >
                <RefreshCw size={16} className={isRefetching ? "animate-spin" : ""} /> 
                {isRefetching ? "Refetching..." : "Refetch Title"}
              </Button>

              {/* Archive Toggle */}
              <Button
                onClick={handleArchiveToggle}
                className="w-full flex items-center justify-center gap-2 bg-muted/50 border border-border hover:bg-muted text-foreground"
              >
                <Archive size={16} /> 
                {bookmark.isArchived ? "Unarchive" : "Archive Link"}
              </Button>

              <div className="pt-2 border-t border-border" />

              {/* Delete */}
              <Button
                onClick={handleDelete}
                className="w-full flex items-center justify-center gap-2 bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                <Trash2 size={16} /> Delete Bookmark
              </Button>
            </div>

            {/* Metadata Stats */}
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Properties
              </h3>

              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <Calendar size={14} className="shrink-0" />
                <div>
                  <p className="font-semibold text-foreground/80">Created</p>
                  <p className="text-[10px] mt-0.5">{formatDateString(bookmark.createdAt)}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <Clock size={14} className="shrink-0" />
                <div>
                  <p className="font-semibold text-foreground/80">Last Checked</p>
                  <p className="text-[10px] mt-0.5">{formatDateString(bookmark.lastCheckedAt)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Form Modal */}
      <BookmarkFormModal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSuccess={() => loadBookmark(false)}
        initialData={bookmark}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Permanently Delete Bookmark?"
        description="Are you sure you want to permanently delete this bookmark? This is a hard delete and cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={isDeleting}
      />
    </DashboardLayout>
  );
};

export default BookmarkDetailPage;
export { BookmarkDetailPage };
