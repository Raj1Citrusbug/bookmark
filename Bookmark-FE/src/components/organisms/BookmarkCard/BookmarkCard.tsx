import { Link } from "react-router-dom";
import type { Bookmark } from "@/types/bookmark";
import { 
  Archive, 
  Trash2, 
  Edit3, 
  ExternalLink, 
  AlertTriangle,
  FileText
} from "lucide-react";
import { cn } from "@/lib/utils";

interface BookmarkCardProps {
  bookmark: Bookmark;
  onArchiveToggle: (id: string) => void;
  onEdit: (bookmark: Bookmark) => void;
  onDelete: (id: string) => void;
}

const BookmarkCard = ({
  bookmark,
  onArchiveToggle,
  onEdit,
  onDelete,
}: BookmarkCardProps) => {
  const displayTitle = bookmark.title || "Fetching title...";
  const isFetchingTitle = !bookmark.title;

  return (
    <div
      className={cn(
        "group relative flex flex-col bg-card hover:bg-card/90 border rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-300",
        bookmark.isBroken 
          ? "border-destructive/50 ring-1 ring-destructive/20" 
          : "border-border hover:border-spanish-gray/40"
      )}
    >
      {/* Broken status header badge */}
      {bookmark.isBroken && (
        <div className="absolute -top-3 left-4 flex items-center gap-1 bg-destructive text-destructive-foreground px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm z-10 animate-pulse">
          <AlertTriangle size={10} />
          <span>Broken Link</span>
        </div>
      )}

      {/* Title & external link */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <a
          href={bookmark.url}
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            "font-display font-extrabold text-base leading-snug hover:text-gold-yellow transition-colors break-all flex-1 min-w-0 pr-2",
            isFetchingTitle ? "text-muted-foreground italic font-medium" : "text-foreground"
          )}
        >
          {displayTitle}
        </a>
        <a
          href={bookmark.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-spanish-gray hover:text-foreground p-1 rounded-md hover:bg-muted shrink-0"
        >
          <ExternalLink size={16} />
        </a>
      </div>

      {/* URL text */}
      <p className="text-xs text-spanish-gray/95 font-sans truncate mb-3 break-all max-w-[90%]">
        {bookmark.url}
      </p>

      {/* Notes snippet */}
      {bookmark.notes && (
        <p className="text-sm font-sans text-muted-foreground leading-relaxed line-clamp-2 mb-4">
          {bookmark.notes}
        </p>
      )}

      {/* Tags badges */}
      {bookmark.tags && bookmark.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4">
          {bookmark.tags.map((tag) => (
            <span
              key={tag.id}
              className="px-2 py-0.5 rounded bg-muted/65 text-muted-foreground font-semibold text-[10px] border border-border/40"
            >
              #{tag.name}
            </span>
          ))}
        </div>
      )}

      {/* Push content down */}
      <div className="flex-1 min-h-[10px]" />

      {/* Broken reason check */}
      {bookmark.isBroken && bookmark.brokenReason && (
        <p className="text-[11px] font-medium text-destructive mb-4 italic">
          Reason: {bookmark.brokenReason}
        </p>
      )}

      {/* Bottom action panel */}
      <div className="flex items-center justify-between border-t border-border/60 pt-3 mt-auto">
        <Link
          to={`/bookmarks/${bookmark.id}`}
          className="flex items-center gap-1 text-xs font-semibold text-spanish-gray hover:text-foreground hover:underline transition-all"
        >
          <FileText size={14} />
          <span>Details</span>
        </Link>

        <div className="flex items-center gap-1">
          {/* Toggle Archive */}
          <button
            onClick={() => onArchiveToggle(bookmark.id)}
            title={bookmark.isArchived ? "Unarchive Bookmark" : "Archive Bookmark"}
            className={cn(
              "p-2 rounded-lg border border-border text-spanish-gray hover:text-foreground hover:bg-muted transition-all",
              bookmark.isArchived && "bg-muted text-foreground"
            )}
          >
            <Archive size={14} />
          </button>

          {/* Edit */}
          <button
            onClick={() => onEdit(bookmark)}
            title="Edit Bookmark"
            className="p-2 rounded-lg border border-border text-spanish-gray hover:text-foreground hover:bg-muted transition-all"
          >
            <Edit3 size={14} />
          </button>

          {/* Delete */}
          <button
            onClick={() => onDelete(bookmark.id)}
            title="Delete Bookmark"
            className="p-2 rounded-lg border border-border/50 text-destructive/80 hover:text-destructive hover:bg-destructive/10 transition-all"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

export { BookmarkCard };
export type { BookmarkCardProps };
