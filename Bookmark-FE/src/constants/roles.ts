export const ROLES = {
  USER: "USER",
  ADMIN: "ADMIN",
} as const;

export type UserRole = typeof ROLES[keyof typeof ROLES];

export const ROLE_DASHBOARDS: Record<UserRole, string> = {
  [ROLES.USER]: "/",
  [ROLES.ADMIN]: "/admin/broken-links",
};
