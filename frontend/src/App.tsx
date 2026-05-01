import type { FC } from "react";
import { Route, Routes } from "react-router";

import DefaultLayout from "./components/layouts/DefaultLayout";
import IndexPage from "./pages/IndexPage";
import NotFoundPage from "./pages/NotFoundPage";
import SigninPage from "./pages/SigninPage";
import SignupPage from "./pages/SignupPage";

interface AppProps {}

const App: FC<AppProps> = () => {
  return (
    <Routes>
      <Route element={<DefaultLayout />}>
        <Route path="/" element={<IndexPage />} />
        <Route path="signin" element={<SigninPage />} />
        <Route path="signup" element={<SignupPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default App;
