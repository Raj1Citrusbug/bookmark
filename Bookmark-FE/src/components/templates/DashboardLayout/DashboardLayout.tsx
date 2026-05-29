import React from "react";
import { useSelector } from "react-redux";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { 
  Bookmark as BookmarkIcon, 
  Archive, 
  ShieldAlert, 
  LogOut, 
  ChevronLeft, 
  ChevronRight, 
  User as UserIcon
} from "lucide-react";
import type { RootState } from "@/store";
import { useAppDispatch } from "@/store";
import { logout, setSidebarCollapsed } from "@/store/slices/authSlice";
import { ROLES } from "@/constants/roles";
import { cn } from "@/lib/utils";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { user, isSidebarCollapsed } = useSelector((state: RootState) => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  const isActive = (path: string) => {
    if (path === "/") {
      return location.pathname === "/" && !location.search.includes("archived=true");
    }
    if (path === "/archived") {
      return location.search.includes("archived=true");
    }
    return location.pathname.startsWith(path);
  };

  const isAdmin = user?.role === ROLES.ADMIN;

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "relative flex flex-col bg-eerie-black text-ivory transition-all duration-300 ease-in-out border-r border-sidebar-border z-20",
          isSidebarCollapsed ? "w-16" : "w-64"
        )}
      >
        {/* Header */}
        <div className={cn(
          "flex h-16 items-center border-b border-sidebar-border transition-all duration-300",
          isSidebarCollapsed ? "justify-center px-0" : "justify-between px-4"
        )}>
          <Link to="/" className="flex items-center gap-3 min-w-0">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gold-yellow text-eerie-black font-display font-extrabold shadow-md animate-in fade-in duration-300">
              B
            </div>
            {!isSidebarCollapsed && (
              <span className="font-display font-bold text-base tracking-wide uppercase truncate">
                Bookmark Manager
              </span>
            )}
          </Link>
          {!isSidebarCollapsed && (
            <button
              onClick={() => dispatch(setSidebarCollapsed(true))}
              className="rounded p-1 hover:bg-space text-spanish-gray hover:text-white shrink-0"
            >
              <ChevronLeft size={18} />
            </button>
          )}
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 p-2 mt-4 overflow-y-auto">
          {/* Active Bookmarks */}
          <Link
            to="/"
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
              isActive("/") 
                ? "bg-gold-yellow text-eerie-black font-semibold" 
                : "text-spanish-gray hover:bg-space hover:text-white"
            )}
          >
            <BookmarkIcon size={18} />
            {!isSidebarCollapsed && <span>My Bookmarks</span>}
          </Link>

          {/* Archived Bookmarks */}
          <Link
            to="/?archived=true"
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
              isActive("/archived") 
                ? "bg-gold-yellow text-eerie-black font-semibold" 
                : "text-spanish-gray hover:bg-space hover:text-white"
            )}
          >
            <Archive size={18} />
            {!isSidebarCollapsed && <span>Archive</span>}
          </Link>

          {/* Admin broken links */}
          {isAdmin && (
            <Link
              to="/admin/broken-links"
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                isActive("/admin/broken-links") 
                  ? "bg-gold-yellow text-eerie-black font-semibold" 
                  : "text-spanish-gray hover:bg-space hover:text-white"
              )}
            >
              <ShieldAlert size={18} />
              {!isSidebarCollapsed && <span>Admin Dashboard</span>}
            </Link>
          )}
        </nav>

        {/* Footer profile & logout */}
        <div className="p-2 border-t border-sidebar-border space-y-1">
          {!isSidebarCollapsed && user && (
            <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-space/35 mb-2">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-spanish-gray/30 text-white">
                <UserIcon size={16} />
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold truncate">{user.name}</p>
                <p className="text-[10px] text-spanish-gray truncate">{user.email}</p>
              </div>
            </div>
          )}

          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-destructive hover:bg-destructive/10 transition-all"
          >
            <LogOut size={18} />
            {!isSidebarCollapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header Bar */}
        <header className="flex h-16 w-full items-center justify-between px-6 border-b border-border bg-card">
          <div className="flex items-center gap-4">
            {isSidebarCollapsed && (
              <button
                onClick={() => dispatch(setSidebarCollapsed(false))}
                className="rounded-lg p-2 hover:bg-muted border border-border text-foreground transition-all"
              >
                <ChevronRight size={18} />
              </button>
            )}
            <h2 className="text-xl font-display font-extrabold text-foreground tracking-tight">
              {location.pathname === "/" && !location.search.includes("archived=true") && "Active Bookmarks"}
              {location.search.includes("archived=true") && "Archived Bookmarks"}
              {location.pathname.startsWith("/bookmarks/") && "Bookmark Details"}
              {location.pathname === "/admin/broken-links" && "Admin Broken Links"}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/60 text-xs font-semibold text-muted-foreground border border-border/55">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Role: {user?.role}
            </div>
          </div>
        </header>

        {/* Viewport content */}
        <main className="flex-1 overflow-y-auto p-6 bg-background">
          <div className="max-w-7xl mx-auto h-full animate-in fade-in slide-in-from-bottom-3 duration-400">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export { DashboardLayout };
