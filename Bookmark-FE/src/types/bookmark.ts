import type { Tag, ApiTag } from "./tag";

export interface Bookmark {
  id: string;
  userId: string;
  url: string;
  title: string | null;
  notes: string | null;
  isArchived: boolean;
  isBroken: boolean;
  brokenReason: string | null;
  lastCheckedAt: string | null;
  tags: Tag[];
  createdAt: string;
  updatedAt: string;
}

export interface ApiBookmark {
  id: string;
  user_id: string;
  url: string;
  title: string | null;
  notes: string | null;
  is_archived: boolean;
  is_broken: boolean;
  broken_reason: string | null;
  last_checked_at: string | null;
  tags: ApiTag[];
  created_at: string;
  updated_at: string;
}

export interface IBookmarkCreateRequest {
  url: string;
  title?: string | null;
  notes?: string | null;
  tags?: string[]; // Tag UUIDs
}

export interface IBookmarkUpdateRequest {
  title?: string | null;
  notes?: string | null;
  tags?: string[]; // Tag UUIDs
}

export interface IBookmarkQueryParams {
  search?: string;
  tag?: string;
  archived?: boolean;
  page?: number;
  limit?: number;
  sort_order?: "asc" | "desc";
}

export interface AdminBrokenLink {
  bookmarkId: string;
  bookmarkTitle: string | null;
  bookmarkUrl: string;
  ownerName: string;
  ownerEmail: string;
  lastCheckedAt: string | null;
  brokenReason: string | null;
}

export interface ApiAdminBrokenLink {
  bookmark_id: string;
  bookmark_title: string | null;
  bookmark_url: string;
  owner_name: string;
  owner_email: string;
  last_checked_at: string | null;
  broken_reason: string | null;
}
