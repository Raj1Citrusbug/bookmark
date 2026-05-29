import { ROLES, ROLE_DASHBOARDS } from "@/constants/roles";
import type { User } from "@/types/user";

/**
 * Returns the primary dashboard path for a user based on their role.
 */
export const getUserDashboard = (user: User | null): string => {
  if (!user || !user.role) return "/login";
  return ROLE_DASHBOARDS[user.role] || "/";
};

/**
 * Checks path access and returns a redirect path if forbidden, or null if allowed.
 */
export const getRedirectIfForbidden = (user: User | null, currentPath: string): string | null => {
  if (!user) return "/login";

  const dashboard = getUserDashboard(user);
  if (currentPath === dashboard) return null;

  // Protect /admin routes
  if (currentPath.startsWith("/admin")) {
    const isAdmin = user.role === ROLES.ADMIN;
    return isAdmin ? null : dashboard;
  }

  return null;
};
