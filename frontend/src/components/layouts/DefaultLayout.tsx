import { type FC } from "react";
import { Outlet } from "react-router";

import style from "./DefaultLayout.module.css";

interface DefaultLayoutProps {}

const DefaultLayout: FC<DefaultLayoutProps> = () => {
  return (
    <div className={style.layout}>
      <Outlet />
    </div>
  );
};

export default DefaultLayout;
