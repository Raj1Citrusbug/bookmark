import { useCallback } from "react";
import type { AxiosResponse } from "axios";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { ToastFail } from "@/utils/helpers";
import { getUserDashboard } from "@/utils/rbac";
import type { RootState } from "@/store";
import { logout as logoutAction } from "@/store/slices/authSlice";

export const handleCommonError = (message: string) => {
  ToastFail(message);
};

export const handle500Error = () => {
  ToastFail("An internal server error occurred. Please try again later.");
};

export interface ErrorResponse {
  response: {
    data: {
      success?: boolean;
      message: string;
    };
    status: number;
  };
}

export const useApiCall = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);

  const call = useCallback(
    async <T>(
      apiCall: () => Promise<AxiosResponse<T>>,
      onSuccess: (response: AxiosResponse<T>) => void,
      onError?: (error: ErrorResponse) => void,
      onFinally?: () => void
    ) => {
      const pathName = window.location.pathname;
      try {
        const response = await apiCall();
        if (!response && pathName !== "/login") {
          return;
        }
        if (response) {
          const { status } = response;
          switch (status) {
            case 200:
            case 201:
            case 202:
              onSuccess(response);
              break;
            default:
              if (onError) onError(response as any);
              break;
          }
        }
      } catch (err: any) {
        const error = err as ErrorResponse;
        const { response } = error;
        if (response) {
          const { status, data } = response;
          const errorMessage = data?.message || "An unexpected error occurred.";
          
          switch (status) {
            case 400:
              handleCommonError(errorMessage);
              break;
            case 401:
              handleCommonError(errorMessage || "Session expired. Please login again.");
              if (window.location.pathname === "/login" || !user) {
                return;
              }
              dispatch(logoutAction());
              navigate("/login");
              break;
            case 403:
              {
                const dashboardPath = getUserDashboard(user);
                navigate(dashboardPath);
                handleCommonError(errorMessage || "You do not have permission to access this resource.");
              }
              break;
            case 404:
              handleCommonError(errorMessage);
              break;
            case 409:
              handleCommonError(errorMessage);
              break;
            case 422:
              handleCommonError(errorMessage);
              break;
            case 429:
              handleCommonError(errorMessage);
              break;
            case 500:
              handle500Error();
              break;
            default:
              handleCommonError(errorMessage);
              break;
          }
        } else {
          handleCommonError("Network error. Please check your connection.");
        }
        if (onError) onError(error);
      } finally {
        if (onFinally) onFinally();
      }
    },
    [user, dispatch, navigate]
  );

  return { call };
};
