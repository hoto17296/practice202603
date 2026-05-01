import { useEffect, useState, type FC } from "react";
import { Link, useParams } from "react-router";

import api, { type ApiSchemaTypes } from "../lib/api";
import { useSession } from "../lib/auth";

interface ArticleDetailPageProps {}

const ArticleDetailPage: FC<ArticleDetailPageProps> = () => {
  useSession();
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<ApiSchemaTypes["ArticleTable"] | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) return;
    api
      .GET("/api/articles/{article_id}", { params: { path: { article_id: id } } })
      .then(({ data, response, error }) => {
        if (response.status === 404) {
          setNotFound(true);
          return;
        }
        if (error) throw error;
        setArticle(data ?? null);
      });
  }, [id]);

  if (notFound) {
    return (
      <>
        <p>記事が見つかりませんでした。</p>
        <p>
          <Link to="/">トップへ戻る</Link>
        </p>
      </>
    );
  }

  if (!article) {
    return <p>読み込み中...</p>;
  }

  return (
    <>
      <p>
        <Link to="/">← 一覧に戻る</Link>
      </p>
      <h2>{article.title}</h2>
      <p style={{ color: "var(--color-note)", fontSize: "0.85em" }}>
        {article.created_at ? new Date(article.created_at).toLocaleString("ja-JP") : ""}
      </p>
      <div style={{ whiteSpace: "pre-wrap", marginTop: "1em" }}>{article.body}</div>
    </>
  );
};

export default ArticleDetailPage;
