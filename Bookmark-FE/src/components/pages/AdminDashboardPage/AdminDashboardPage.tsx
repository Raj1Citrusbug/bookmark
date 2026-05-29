import { useState, useEffect } from "react";
import { adminBrokenLinks } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { DashboardLayout } from "@/components/templates";
import { Button } from "@/components/atoms";
import type { AdminBrokenLink } from "@/types/bookmark";
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  AlertTriangle, 
  User as UserIcon, 
  ExternalLink,
  ShieldCheck
} from "lucide-react";
import { format } from "date-fns";

const AdminDashboardPage = () => {
  const { call } = useApiCall();

  // Search & filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [activeSearch, setActiveSearch] = useState("");
  const [brokenLinks, setBrokenLinks] = useState<AdminBrokenLink[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [isLoading, setIsLoading] = useState(true);

  const loadBrokenLinks = () => {
    setIsLoading(true);
    const queryParams = {
      search: activeSearch || undefined,
      page,
      limit,
      sort_order: "desc",
    };

    call(
      () => adminBrokenLinks(queryParams),
      (response) => {
        // Transform api payload to camelCase
        const list = (response.data.data || []).map((apiItem: any) => ({
          bookmarkId: apiItem.bookmark_id,
          bookmarkTitle: apiItem.bookmark_title,
          bookmarkUrl: apiItem.bookmark_url,
          ownerName: apiItem.owner_name,
          ownerEmail: apiItem.owner_email,
          lastCheckedAt: apiItem.last_checked_at,
          brokenReason: apiItem.broken_reason,
        }));
        setBrokenLinks(list);
        setTotalCount(response.data.count || 0);
      },
      undefined,
      () => setIsLoading(false)
    );
  };

  useEffect(() => {
    loadBrokenLinks();
  }, [activeSearch, page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveSearch(searchQuery);
    setPage(1); // reset to page 1
  };

  const totalPages = Math.ceil(totalCount / limit) || 1;
  const handlePrevPage = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleNextPage = () => {
    if (page < totalPages) setPage(page + 1);
  };

  const formatDateString = (dateStr: string | null) => {
    if (!dateStr) return "Never";
    try {
      return format(new Date(dateStr), "MMM d, yyyy 'at' p");
    } catch (e) {
      return "Invalid Date";
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Banner Card */}
        <div className="flex items-center gap-4 bg-eerie-black text-white p-6 rounded-xl shadow-md border border-sidebar-border relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 rounded-full bg-gold-yellow/5 blur-[50px] pointer-events-none" />
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gold-yellow/20 text-gold-yellow">
            <AlertTriangle size={24} />
          </div>
          <div>
            <h1 className="text-xl font-display font-extrabold tracking-tight">System-Wide Broken Links</h1>
            <p className="text-sm text-spanish-gray mt-1 leading-relaxed">
              Global dashboard monitoring inaccessible links and failure response codes across the system.
            </p>
          </div>
        </div>

        {/* Metric Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card border border-border p-5 rounded-xl shadow-sm">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Failed URLs Found
            </h3>
            <p className="text-3xl font-display font-black mt-2 text-destructive">
              {totalCount}
            </p>
          </div>
          <div className="bg-card border border-border p-5 rounded-xl shadow-sm">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Access Role Check
            </h3>
            <p className="text-3xl font-display font-black mt-2 text-foreground flex items-center gap-2">
              <ShieldCheck className="text-emerald-500" size={28} />
              <span>Admin Audit</span>
            </p>
          </div>
        </div>

        {/* Controls Panel */}
        <div className="flex items-center gap-4 bg-card border border-border p-4 rounded-xl shadow-sm">
          <form onSubmit={handleSearchSubmit} className="relative flex-1">
            <input
              type="text"
              placeholder="Search by title, url, owner name, owner email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 rounded-lg border border-input bg-background text-sm shadow-sm transition-all focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
            />
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
          </form>
        </div>

        {/* Broken Links Audit Table */}
        <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/30 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <th className="p-4 pl-6">Bookmark Title</th>
                  <th className="p-4">Owner Account</th>
                  <th className="p-4">Last Verified</th>
                  <th className="p-4 pr-6">Failure Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-sm">
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="p-4 pl-6"><div className="h-4 bg-muted rounded w-48" /></td>
                      <td className="p-4"><div className="h-4 bg-muted rounded w-32" /></td>
                      <td className="p-4"><div className="h-4 bg-muted rounded w-32" /></td>
                      <td className="p-4 pr-6"><div className="h-4 bg-muted rounded w-40" /></td>
                    </tr>
                  ))
                ) : brokenLinks.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-12 text-center text-muted-foreground italic">
                      No broken bookmarks found in the database.
                    </td>
                  </tr>
                ) : (
                  brokenLinks.map((link) => (
                    <tr key={link.bookmarkId} className="hover:bg-muted/10 transition-colors">
                      <td className="p-4 pl-6">
                        <div className="flex flex-col gap-1 max-w-sm md:max-w-md">
                          <span className="font-semibold text-foreground truncate">
                            {link.bookmarkTitle || <span className="text-muted-foreground italic font-medium">Untitled</span>}
                          </span>
                          <a
                            href={link.bookmarkUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary hover:underline flex items-center gap-1 break-all truncate"
                          >
                            <span>{link.bookmarkUrl}</span>
                            <ExternalLink size={10} className="shrink-0" />
                          </a>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <UserIcon size={14} className="text-spanish-gray" />
                          <div className="flex flex-col">
                            <span className="font-medium text-foreground">{link.ownerName}</span>
                            <span className="text-[10px] text-muted-foreground">{link.ownerEmail}</span>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-xs text-muted-foreground">
                        {formatDateString(link.lastCheckedAt)}
                      </td>
                      <td className="p-4 pr-6">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-destructive/10 text-destructive text-xs font-semibold font-sans">
                          {link.brokenReason || "Unknown connection error"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-border/80 bg-muted/10">
              <span className="text-xs text-muted-foreground font-semibold">
                Showing {brokenLinks.length} of {totalCount} records
              </span>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePrevPage}
                  disabled={page === 1}
                  className="flex items-center gap-1"
                >
                  <ChevronLeft size={16} /> Prev
                </Button>

                <div className="text-xs font-semibold px-3 py-2 border border-border rounded-lg bg-card text-foreground">
                  Page {page} of {totalPages}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNextPage}
                  disabled={page === totalPages}
                  className="flex items-center gap-1"
                >
                  Next <ChevronRight size={16} />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboardPage;
export { AdminDashboardPage };
