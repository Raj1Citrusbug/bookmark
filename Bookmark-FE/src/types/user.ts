import type { UserRole } from "@/constants/roles";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  isActive: boolean;
}

export interface ApiUser {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface ILoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface IRegisterRequest {
  name: string;
  email: string;
  password: string;
}

/**
 * Returns true if the user holds the allowed roles.
 * Canonical checker matching LMS-FE.
 */
export const userHasRole = (
  user: User | null,
  allowedRoles: UserRole[]
): boolean => {
  if (!user || !user.role) return false;
  return allowedRoles.includes(user.role);
};
