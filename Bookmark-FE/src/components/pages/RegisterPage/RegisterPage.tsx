import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { registerFormSchema, type RegisterFormData } from "@/constants/schemas/auth";
import { registerUser } from "@/network";
import { useApiCall } from "@/hooks/useApiCall";
import { ToastSuccess } from "@/utils/helpers";
import { AuthLayout } from "@/components/templates";
import { Button } from "@/components/atoms";
import { FormField } from "@/components/molecules";

const RegisterPage = () => {
  const navigate = useNavigate();
  const { call } = useApiCall();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { control, handleSubmit } = useForm<RegisterFormData>({
    resolver: zodResolver(registerFormSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    setIsSubmitting(true);
    call(
      () => registerUser({
        name: data.name,
        email: data.email,
        password: data.password,
      }),
      () => {
        ToastSuccess("Account created successfully! Please sign in.");
        navigate("/login");
      },
      undefined,
      () => setIsSubmitting(false)
    );
  };

  return (
    <AuthLayout title="Get Started" subtitle="Create your account to save bookmarks">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={control}
          name="name"
          label="Full Name"
          type="text"
          placeholder="e.g. Raj"
          disabled={isSubmitting}
        />

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

        <FormField
          control={control}
          name="confirmPassword"
          label="Confirm Password"
          type="password"
          placeholder="••••••••"
          disabled={isSubmitting}
        />

        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full h-11 bg-gold-yellow hover:bg-gold-yellow/90 text-eerie-black font-semibold rounded-lg shadow-lg hover:shadow-gold-yellow/10"
        >
          {isSubmitting ? "Creating Account..." : "Sign Up"}
        </Button>

        <p className="text-center text-sm text-spanish-gray mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-white hover:text-gold-yellow font-semibold underline transition-all">
            Sign In
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
};

export default RegisterPage;
export { RegisterPage };
