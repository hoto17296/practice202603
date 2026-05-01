import { useEffect, useState, type FC } from "react";
import { Link, useNavigate, useParams } from "react-router";

import api, { type ApiSchemaTypes } from "../lib/api";
import { useSession } from "../lib/auth";

interface ArticleDetailPageProps {}

const ArticleDetailPage: FC<ArticleDetailPageProps> = () => {
  const session = useSession();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [article, setArticle] = useState<ApiSchemaTypes["ArticleDetail"] | null>(null);
  const [notFound, setNotFound] = useState(false);

  async function handleDelete() {
    if (!id || !window.confirm("この記事を削除しますか？")) return;
    const { response, error } = await api.DELETE("/api/articles/{article_id}", {
      params: { path: { article_id: id } },
    });
    if (!response.ok) throw error;
    navigate("/");
  }

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
        {article.author_id === session.user.id && (
          <>
            {" "}
            · <Link to={`/article/${id}/edit`}>編集</Link> ·{" "}
            <a href="#" onClick={handleDelete}>
              削除
            </a>
          </>
        )}
      </p>
      <h2>{article.title}</h2>
      <p style={{ color: "var(--color-note)", fontSize: "0.85em" }}>
        {article.author_name} ·{" "}
        {article.published_at ? new Date(article.published_at).toLocaleString("ja-JP") : ""}
      </p>
      <div style={{ whiteSpace: "pre-wrap", marginTop: "1em" }}>{article.body}</div>
    </>
  );
};

export default ArticleDetailPage;
