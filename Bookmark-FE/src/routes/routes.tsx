import { createBrowserRouter, Navigate } from "react-router-dom";
import { PrivateRoutes } from "./PrivateRoutes";
import { PublicRoutes } from "./PublicRoutes";
import { ROLES } from "@/constants/roles";

// Pages
import LoginPage from "@/components/pages/LoginPage/LoginPage";
import RegisterPage from "@/components/pages/RegisterPage/RegisterPage";
import BookmarksPage from "@/components/pages/BookmarksPage/BookmarksPage";
import BookmarkDetailPage from "@/components/pages/BookmarkDetailPage/BookmarkDetailPage";
import AdminDashboardPage from "@/components/pages/AdminDashboardPage/AdminDashboardPage";

export const router = createBrowserRouter([
  // Public Auth Routes
  {
    element: <PublicRoutes />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
    ],
  },
  
  // Guarded User Routes
  {
    element: <PrivateRoutes allowedRoles={[ROLES.USER, ROLES.ADMIN]} />,
    children: [
      { path: "/", element: <BookmarksPage /> },
      { path: "/bookmarks/:id", element: <BookmarkDetailPage /> },
    ],
  },

  // Guarded Admin Only Routes
  {
    element: <PrivateRoutes allowedRoles={[ROLES.ADMIN]} />,
    children: [
      { path: "/admin/broken-links", element: <AdminDashboardPage /> },
    ],
  },

  // Fallback Catch All
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);
