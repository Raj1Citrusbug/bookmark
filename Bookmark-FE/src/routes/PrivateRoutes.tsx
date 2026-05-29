import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Navigate, Outlet, useLocation, useNavigate } from "react-router-dom";
import type { UserRole } from "@/constants/roles";
import type { RootState } from "@/store";
import { userHasRole } from "@/types/user";
import { getUserDashboard, getRedirectIfForbidden } from "@/utils/rbac";
import { Loading, Button } from "@/components/atoms";
import { removeToken } from "@/utils/cookie";

interface PrivateRoutesProps {
  allowedRoles?: UserRole[];
}

const PrivateRoutes = ({ allowedRoles }: PrivateRoutesProps) => {
  const { isAuthenticated, user, isLoading } = useSelector(
    (state: RootState) => state.auth
  );
  const location = useLocation();
  const navigate = useNavigate();
  const [takeTooLong, setTakeTooLong] = useState<boolean>(false);

  useEffect(() => {
    let timer: any;
    if (isLoading || (isAuthenticated && !user)) {
      timer = setTimeout(() => {
        setTakeTooLong(true);
      }, 10000);
    }
    return () => clearTimeout(timer);
  }, [isLoading, isAuthenticated, user]);

  const handleGoToLogin = () => {
    removeToken();
    navigate("/login");
  };

  if (isLoading || (isAuthenticated && !user)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-background text-center px-4">
        <Loading variant="page" text="Verifying session..." />
        {takeTooLong && (
          <div className="fixed inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm z-[110] animate-in fade-in duration-500">
            <div className="max-w-sm w-full bg-card text-card-foreground p-6 rounded-xl shadow-2xl border border-border animate-in zoom-in-95 duration-300">
              <h3 className="text-xl font-bold mb-2">Oops! Something went wrong</h3>
              <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                We're having trouble verifying your session. This could be due to a slow connection or an expired session.
              </p>
              <div className="flex flex-col gap-2">
                <Button 
                  onClick={() => window.location.reload()} 
                  className="w-full font-semibold h-11 rounded-xl"
                >
                  Try Again
                </Button>
                <Button 
                  variant="outline"
                  onClick={handleGoToLogin} 
                  className="w-full font-semibold h-11 rounded-xl"
                >
                  Back to Login
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Generic Role Check
  if (allowedRoles && !userHasRole(user, allowedRoles)) {
    return <Navigate to={getUserDashboard(user)} replace />;
  }

  // Path-Specific Redirect Logic
  const redirectPath = getRedirectIfForbidden(user, location.pathname);
  if (redirectPath) {
    return <Navigate to={redirectPath} replace />;
  }

  return <Outlet />;
};

export { PrivateRoutes };
