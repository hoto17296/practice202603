import { useEffect, useState, type FC } from "react";
import { Link } from "react-router";

import api, { type ApiSchemaTypes } from "../lib/api";
import { signout, useSession } from "../lib/auth";

interface IndexPageProps {}

const IndexPage: FC<IndexPageProps> = () => {
  const session = useSession();
  const [articles, setArticles] = useState<ApiSchemaTypes["ArticleSummary"][]>([]);

  useEffect(() => {
    api.GET("/api/articles/").then(({ data, error }) => {
      if (error) throw error;
      setArticles(data ?? []);
    });
  }, []);

  return (
    <>
      <h2>Top page</h2>
      <p>Hello, {session.user.name}!</p>
      <p>
        <Link to="/article/new">新しい記事を書く</Link>
      </p>

      <h3>記事一覧</h3>
      {articles.length === 0 ? (
        <p>まだ記事がありません。</p>
      ) : (
        <ul>
          {articles.map((article) => (
            <li key={article.id}>
              <Link to={`/article/${article.id}`}>{article.title}</Link>
              <span style={{ marginLeft: "1em", color: "var(--color-note)", fontSize: "0.85em" }}>
                {article.author_name} · {new Date(article.published_at).toLocaleString("ja-JP")}
              </span>
            </li>
          ))}
        </ul>
      )}

      <p>
        <a href="#" onClick={signout}>
          Sign out
        </a>
      </p>
    </>
  );
};

export default IndexPage;
