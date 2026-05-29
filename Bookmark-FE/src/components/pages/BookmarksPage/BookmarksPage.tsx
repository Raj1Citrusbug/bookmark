import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { getBookmarks, getTagCloud, archiveBookmark, deleteBookmark } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { ToastSuccess } from "@/utils/helpers";
import { DashboardLayout } from "@/components/templates";
import { BookmarkCard, BookmarkFormModal, TagCreateModal } from "@/components/organisms";
import { Button } from "@/components/atoms";
import { ConfirmationModal } from "@/components/molecules";
import type { Bookmark } from "@/types/bookmark";
import type { TagCloudData } from "@/types/tag";
import { 
  Search, 
  Plus, 
  Tag as TagIcon, 
  FolderOpen, 
  ChevronLeft, 
  ChevronRight, 
  RotateCcw
} from "lucide-react";

const BookmarksPage = () => {
  const { call } = useApiCall();
  const [searchParams, setSearchParams] = useSearchParams();

  // URL search states
  const searchParam = searchParams.get("search") || "";
  const tagParam = searchParams.get("tag") || "";
  const pageParam = parseInt(searchParams.get("page") || "1", 10);
  const isArchived = searchParams.get("archived") === "true";

  // Local UI states
  const [searchQuery, setSearchQuery] = useState(searchParam);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [tagCloud, setTagCloud] = useState<TagCloudData[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [limit] = useState(9); // 9 per page for a nice 3x3 grid

  // Modals state
  const [isBookmarkModalOpen, setIsBookmarkModalOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
  const [selectedBookmarkForEdit, setSelectedBookmarkForEdit] = useState<Bookmark | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [bookmarkIdToDelete, setBookmarkIdToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Polling ref for title updates
  const pollingIntervalRef = useRef<any>(null);

  // Sync local search query state with URL
  useEffect(() => {
    setSearchQuery(searchParam);
  }, [searchParam]);

  // Load Bookmarks and Tag Cloud
  const loadData = (showLoader = true) => {
    if (showLoader) setIsLoading(true);

    const queryParams = {
      search: searchParam || undefined,
      tag: tagParam || undefined,
      archived: isArchived,
      page: pageParam,
      limit,
      sort_order: "desc" as const,
    };

    call(
      () => getBookmarks(queryParams),
      (response) => {
        // Transform api payload to camelCase
        const list = (response.data.data || []).map((apiItem: any) => ({
          id: apiItem.id,
          userId: apiItem.user_id,
          url: apiItem.url,
          title: apiItem.title,
          notes: apiItem.notes,
          isArchived: apiItem.is_archived,
          isBroken: apiItem.is_broken,
          brokenReason: apiItem.broken_reason,
          lastCheckedAt: apiItem.last_checked_at,
          tags: apiItem.tags || [],
          createdAt: apiItem.created_at,
          updatedAt: apiItem.updated_at,
        }));
        setBookmarks(list);
        setTotalCount(response.data.count || 0);
      },
      undefined,
      () => {
        if (showLoader) setIsLoading(false);
      }
    );

    // Load Tag cloud
    call(
      () => getTagCloud(),
      (response) => {
        setTagCloud(response.data.data || []);
      }
    );
  };

  // Trigger reloading whenever query parameters change
  useEffect(() => {
    loadData(true);
  }, [searchParam, tagParam, pageParam, isArchived]);

  // Polling for missing titles (Celery Async Update UX)
  useEffect(() => {
    const hasFetchingTitles = bookmarks.some((b) => !b.title);

    if (hasFetchingTitles && !isArchived) {
      if (!pollingIntervalRef.current) {
        pollingIntervalRef.current = setInterval(() => {
          loadData(false); // poll in background without trigger full page skeleton loaders
        }, 3000);
      }
    } else {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [bookmarks, isArchived]);

  // Handle Search submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (searchQuery) {
        next.set("search", searchQuery);
      } else {
        next.delete("search");
      }
      next.set("page", "1"); // reset to page 1 on new search
      return next;
    });
  };

  // Toggle active / archived filter
  const handleTagFilter = (tagName: string) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (tagParam === tagName) {
        next.delete("tag"); // toggle off
      } else {
        next.set("tag", tagName);
      }
      next.set("page", "1");
      return next;
    });
  };

  // Clear all filters
  const handleClearFilters = () => {
    setSearchQuery("");
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete("search");
      next.delete("tag");
      next.set("page", "1");
      return next;
    });
  };

  // Handle Pagination
  const totalPages = Math.ceil(totalCount / limit) || 1;
  const handlePrevPage = () => {
    if (pageParam > 1) {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        next.set("page", String(pageParam - 1));
        return next;
      });
    }
  };

  const handleNextPage = () => {
    if (pageParam < totalPages) {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        next.set("page", String(pageParam + 1));
        return next;
      });
    }
  };

  // Bookmark actions
  const handleArchiveToggle = (id: string) => {
    call(
      () => archiveBookmark(id),
      () => {
        ToastSuccess(isArchived ? "Bookmark restored to active list." : "Bookmark archived.");
        loadData(false);
      }
    );
  };

  const handleEditInit = (bookmark: Bookmark) => {
    setSelectedBookmarkForEdit(bookmark);
    setIsBookmarkModalOpen(true);
  };

  const handleDeleteBookmark = (id: string) => {
    setBookmarkIdToDelete(id);
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDeleteBookmark = () => {
    if (!bookmarkIdToDelete) return;
    setIsDeleting(true);
    call(
      () => deleteBookmark(bookmarkIdToDelete),
      () => {
        ToastSuccess("Bookmark deleted successfully.");
        loadData(false);
        setIsDeleteModalOpen(false);
        setBookmarkIdToDelete(null);
      },
      undefined,
      () => setIsDeleting(false)
    );
  };

  // Tag Cloud Font Weight Calculator
  const getTagWeightClass = (count: number) => {
    const maxCount = Math.max(...tagCloud.map((t) => t.count), 1);
    const weight = count / maxCount;

    if (weight > 0.8) return "text-lg font-bold text-primary";
    if (weight > 0.5) return "text-sm font-semibold text-foreground/80";
    if (weight > 0.2) return "text-xs font-medium text-muted-foreground";
    return "text-[11px] text-muted-foreground/70";
  };

  return (
    <DashboardLayout>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 h-full">
        {/* Left Filter Sidebar Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Tag Cloud Component */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-border pb-3">
              <h3 className="text-sm font-display font-extrabold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <TagIcon size={14} /> Tag Cloud
              </h3>
              <button
                onClick={() => setIsTagModalOpen(true)}
                className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
              >
                <Plus size={12} /> Add Tag
              </button>
            </div>

            <div className="flex flex-wrap gap-2.5 pt-1">
              {tagCloud.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No tags created yet.</p>
              ) : (
                tagCloud.map((tag) => {
                  const isSelected = tagParam === tag.name;
                  return (
                    <button
                      key={tag.name}
                      onClick={() => handleTagFilter(tag.name)}
                      className={`px-2.5 py-1 rounded-full border transition-all ${
                        isSelected
                          ? "bg-primary border-primary text-primary-foreground scale-105"
                          : "bg-muted/40 border-border/70 hover:bg-muted"
                      } ${getTagWeightClass(tag.count)}`}
                    >
                      #{tag.name} <span className="text-[10px] opacity-70">({tag.count})</span>
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Quick Filters Info */}
          {(searchParam || tagParam) && (
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
              <h3 className="text-sm font-display font-extrabold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
                Active Filters
              </h3>
              <div className="space-y-2">
                {searchParam && (
                  <div className="flex items-center justify-between text-xs bg-muted/50 p-2 rounded border border-border">
                    <span className="truncate">Search: <strong>"{searchParam}"</strong></span>
                  </div>
                )}
                {tagParam && (
                  <div className="flex items-center justify-between text-xs bg-muted/50 p-2 rounded border border-border">
                    <span>Tag: <strong>#{tagParam}</strong></span>
                  </div>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearFilters}
                  className="w-full flex items-center justify-center gap-1.5 mt-2"
                >
                  <RotateCcw size={12} />
                  Clear Filters
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Main View Area */}
        <div className="lg:col-span-3 flex flex-col h-full space-y-6">
          {/* Top Actions Panel */}
          <div className="flex flex-col sm:flex-row items-center gap-4 bg-card border border-border p-4 rounded-xl shadow-sm">
            <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
              <input
                type="text"
                placeholder="Search bookmarks by title or notes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-10 pl-10 pr-4 rounded-lg border border-input bg-background text-sm shadow-sm transition-all focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
              />
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
            </form>

            <div className="flex items-center gap-3 shrink-0 w-full sm:w-auto">
              <Button
                onClick={() => {
                  setSelectedBookmarkForEdit(null);
                  setIsBookmarkModalOpen(true);
                }}
                className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gold-yellow text-eerie-black font-semibold hover:bg-gold-yellow/90 shadow-md shadow-gold-yellow/5"
              >
                <Plus size={16} /> Save URL
              </Button>
            </div>
          </div>

          {/* Bookmarks Grid / List */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 flex-1">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="border border-border/80 rounded-xl p-5 bg-card space-y-4 animate-pulse">
                  <div className="h-5 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                  <div className="h-16 bg-muted rounded w-full" />
                  <div className="flex gap-2">
                    <div className="h-4 bg-muted rounded w-12" />
                    <div className="h-4 bg-muted rounded w-12" />
                  </div>
                  <div className="flex justify-between border-t border-border pt-3">
                    <div className="h-4 bg-muted rounded w-16" />
                    <div className="h-6 bg-muted rounded w-24" />
                  </div>
                </div>
              ))}
            </div>
          ) : bookmarks.length === 0 ? (
            <div className="flex flex-col items-center justify-center bg-card border border-border border-dashed rounded-xl p-12 text-center flex-1">
              <FolderOpen size={48} className="text-spanish-gray/70 mb-4" />
              <h3 className="text-lg font-display font-extrabold mb-1">No bookmarks found</h3>
              <p className="text-sm text-muted-foreground max-w-sm leading-relaxed mb-6">
                {searchParam || tagParam
                  ? "Try resetting your search parameters or select a different tag cloud filter."
                  : "Save URLs here to keep track of your websites. They'll show up in this space."}
              </p>
              {(searchParam || tagParam) ? (
                <Button onClick={handleClearFilters} variant="outline">
                  Reset Search
                </Button>
              ) : (
                <Button onClick={() => setIsBookmarkModalOpen(true)}>Add your first link</Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {bookmarks.map((bookmark) => (
                <BookmarkCard
                  key={bookmark.id}
                  bookmark={bookmark}
                  onArchiveToggle={handleArchiveToggle}
                  onEdit={handleEditInit}
                  onDelete={handleDeleteBookmark}
                />
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-border/80 pt-4 mt-auto">
              <span className="text-xs text-muted-foreground font-semibold">
                Showing {bookmarks.length} of {totalCount} bookmarks
              </span>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePrevPage}
                  disabled={pageParam === 1}
                  className="flex items-center gap-1"
                >
                  <ChevronLeft size={16} /> Prev
                </Button>

                <div className="text-xs font-semibold px-3 py-2 border border-border rounded-lg bg-card text-foreground">
                  Page {pageParam} of {totalPages}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNextPage}
                  disabled={pageParam === totalPages}
                  className="flex items-center gap-1"
                >
                  Next <ChevronRight size={16} />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bookmark Save/Edit Form Modal */}
      <BookmarkFormModal
        isOpen={isBookmarkModalOpen}
        onClose={() => {
          setIsBookmarkModalOpen(false);
          setSelectedBookmarkForEdit(null);
        }}
        onSuccess={loadData}
        initialData={selectedBookmarkForEdit}
      />

      {/* Tag Creation Dialog */}
      <TagCreateModal
        isOpen={isTagModalOpen}
        onClose={() => setIsTagModalOpen(false)}
        onSuccess={loadData}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setBookmarkIdToDelete(null);
        }}
        onConfirm={handleConfirmDeleteBookmark}
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

export default BookmarksPage;
export { BookmarksPage };
