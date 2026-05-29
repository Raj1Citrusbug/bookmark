export const apiEndpoints = {
  // Auth
  register: "/auth/register",
  login: "/auth/login",
  
  // User Profile
  me: "/users/me",

  // Bookmarks
  bookmarks: "/bookmarks",
  bookmarkDetail: (id: string) => `/bookmarks/${id}`,
  archiveBookmark: (id: string) => `/bookmarks/${id}/archive`,
  refetchTitle: (id: string) => `/bookmarks/${id}/refetch-title`,

  // Tags
  tags: "/tags",
  tagCloud: "/tags/cloud",

  // Admin
  adminBrokenLinks: "/admin/broken-links",
};
