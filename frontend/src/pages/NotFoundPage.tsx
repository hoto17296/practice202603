import type { FC } from "react";
import { Link } from "react-router";

interface NotFoundPageProps {}

const NotFoundPage: FC<NotFoundPageProps> = () => {
  return (
    <>
      <h2>Not Found</h2>
      <p>
        <Link to="/">Top page</Link>
      </p>
    </>
  );
};

export default NotFoundPage;
