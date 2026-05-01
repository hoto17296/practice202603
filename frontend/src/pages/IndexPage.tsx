import type { FC } from "react";

import { signout, useSession } from "../lib/auth";

interface IndexPageProps {}

const IndexPage: FC<IndexPageProps> = () => {
  const session = useSession();

  return (
    <>
      <h2>Top page</h2>
      <p>Hello, {session.user.name}!</p>
      <p>
        <a href="#" onClick={signout}>
          Sign out
        </a>
      </p>
    </>
  );
};

export default IndexPage;
