import { useEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { Provider } from "react-redux";
import { Toaster } from "sonner";
import { router } from "@/routes/routes";
import { store } from "@/store";
import { initializeAuth, fetchProfile } from "@/store/slices/authSlice";

function App() {
  useEffect(() => {
    store.dispatch(initializeAuth());
    if (store.getState().auth.token) {
      store.dispatch(fetchProfile());
    }
  }, []);

  return (
    <Provider store={store}>
      <RouterProvider router={router} />
      <Toaster 
        richColors 
        position="top-right"
        theme="light"
        closeButton
      />
    </Provider>
  );
}

export default App;
