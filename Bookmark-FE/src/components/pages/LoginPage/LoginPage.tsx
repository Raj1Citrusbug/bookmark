import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { loginFormSchema, type LoginFormData } from "@/constants/schemas/auth";
import { loginUser } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { setTokenCookieWithExpiryFromToken } from "@/utils/cookie";
import { ToastSuccess } from "@/utils/helpers";
import { useAppDispatch } from "@/store";
import { setAuth, transformApiUser } from "@/store/slices/authSlice";
import { AuthLayout } from "@/components/templates";
import { Button } from "@/components/atoms";
import { FormField } from "@/components/molecules";

const LoginPage = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { call } = useApiCall();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { control, handleSubmit, register } = useForm<LoginFormData>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      email: "",
      password: "",
      remember_me: false,
    },
  });

  const onSubmit = (data: LoginFormData) => {
    setIsSubmitting(true);
    call(
      () => loginUser({
        email: data.email,
        password: data.password,
        remember_me: data.remember_me,
      }),
      (response) => {
        const { access_token, user } = response.data.data;
        setTokenCookieWithExpiryFromToken(access_token);
        const transformedUser = transformApiUser(user);
        dispatch(setAuth({ user: transformedUser, token: access_token }));
        ToastSuccess("Logged in successfully!");
        if (transformedUser.role === "ADMIN") {
          navigate("/admin/broken-links");
        } else {
          navigate("/");
        }
      },
      undefined,
      () => setIsSubmitting(false)
    );
  };

  return (
    <AuthLayout title="Welcome Back" subtitle="Sign in to access your bookmarks">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <FormField
          control={control}
          name="email"
          label="Email Address"
          type="email"
          placeholder="e.g. raj@example.com"
          disabled={isSubmitting}
        />

        <FormField
          control={control}
          name="password"
          label="Password"
          type="password"
          placeholder="••••••••"
          disabled={isSubmitting}
        />

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer select-none text-sm text-spanish-gray">
            <input
              type="checkbox"
              {...register("remember_me")}
              className="w-4 h-4 rounded border-gray-300 text-gold-yellow focus:ring-gold-yellow bg-card"
              disabled={isSubmitting}
            />
            <span>Remember Me</span>
          </label>
        </div>

        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full h-11 bg-gold-yellow hover:bg-gold-yellow/90 text-eerie-black font-semibold rounded-lg shadow-lg hover:shadow-gold-yellow/10"
        >
          {isSubmitting ? "Signing In..." : "Sign In"}
        </Button>

        <p className="text-center text-sm text-spanish-gray mt-6">
          Don't have an account?{" "}
          <Link to="/register" className="text-white hover:text-gold-yellow font-semibold underline transition-all">
            Sign Up
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
};

export default LoginPage;
export { LoginPage };
