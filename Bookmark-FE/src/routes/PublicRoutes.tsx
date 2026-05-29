import { useSelector } from "react-redux";
import { Navigate, Outlet } from "react-router-dom";
import type { RootState } from "@/store";
import { getUserDashboard } from "@/utils/rbac";
import { Loading } from "@/components/atoms";

const PublicRoutes = () => {
  const { isAuthenticated, user, isLoading } = useSelector(
    (state: RootState) => state.auth
  );

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-background text-center px-4">
        <Loading variant="page" text="Verifying session..." />
      </div>
    );
  }

  if (isAuthenticated && user) {
    return <Navigate to={getUserDashboard(user)} replace />;
  }

  return <Outlet />;
};

export { PublicRoutes };
