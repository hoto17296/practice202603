import { useAtomValue } from "jotai";
import { type FC } from "react";
import { Link, Outlet, useLocation } from "react-router";

import { authSessionAtom } from "../../atoms";
import { signout } from "../../lib/auth";

import style from "./DefaultLayout.module.css";

interface DefaultLayoutProps {}

const DefaultLayout: FC<DefaultLayoutProps> = () => {
  const location = useLocation();
  const session = useAtomValue(authSessionAtom);

  return (
    <div className={style.layout}>
      <header className={style.header}>
        <Link to="/" className={style.appName}>
          Practice 2026.03
        </Link>
        <nav className={style.nav}>
          {location.pathname === "/signup" && <Link to="/signin">サインイン</Link>}
          {location.pathname === "/signin" && <Link to="/signup">アカウント登録</Link>}
          {session && (
            <>
              <span style={{ color: "var(--color-note)" }}>ログイン中: {session.user.name}</span>
              <a href="#" onClick={signout}>
                サインアウト
              </a>
            </>
          )}
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default DefaultLayout;
