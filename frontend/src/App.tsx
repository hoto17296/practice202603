import { useAtomValue } from "jotai";
import type { FC } from "react";
import { Navigate, Outlet, Route, Routes } from "react-router";

import { authSessionAtom } from "./atoms";
import DefaultLayout from "./components/layouts/DefaultLayout";
import ArticleDetailPage from "./pages/ArticleDetailPage";
import ArticleEditPage from "./pages/ArticleEditPage";
import ArticleNewPage from "./pages/ArticleNewPage";
import IndexPage from "./pages/IndexPage";
import NotFoundPage from "./pages/NotFoundPage";
import SigninPage from "./pages/SigninPage";
import SignupPage from "./pages/SignupPage";

interface AppProps {}

const App: FC<AppProps> = () => {
  const session = useAtomValue(authSessionAtom);
  return (
    <Routes>
      <Route element={<DefaultLayout />}>
        <Route element={session ? <Navigate to="/" replace /> : <Outlet />}>
          <Route path="signin" element={<SigninPage />} />
          <Route path="signup" element={<SignupPage />} />
        </Route>
        <Route element={session ? <Outlet /> : <Navigate to="/signin" replace />}>
          <Route path="/" element={<IndexPage />} />
          <Route path="article/new" element={<ArticleNewPage />} />
          <Route path="article/:id" element={<ArticleDetailPage />} />
          <Route path="article/:id/edit" element={<ArticleEditPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default App;
