import { DeleteOutlined, EditOutlined } from "@ant-design/icons";
import { Button, Card, Tooltip } from "antd";
import { useEffect, useState, type FC } from "react";
import { Link, useNavigate, useParams } from "react-router";

import api, { type ApiSchemaTypes } from "../lib/api";
import { useSession } from "../lib/auth";
import { formatUnixTimestamp } from "../lib/utils";

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
    <Card>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "0.5em",
        }}
      >
        <h2 style={{ margin: 0 }}>{article.title}</h2>
        {article.author_id === session.user.id && (
          <div style={{ display: "flex", gap: "0.5em" }}>
            <Tooltip title="編集する">
              <Button icon={<EditOutlined />} onClick={() => navigate(`/article/${id}/edit`)} />
            </Tooltip>
            <Tooltip title="削除する">
              <Button danger icon={<DeleteOutlined />} onClick={handleDelete} />
            </Tooltip>
          </div>
        )}
      </div>
      <p style={{ color: "var(--color-note)", fontSize: "0.85em", marginTop: 0 }}>
        {article.author_name} ·{" "}
        {article.published_at ? formatUnixTimestamp(article.published_at) : ""}
      </p>
      <div style={{ whiteSpace: "pre-wrap" }}>{article.body}</div>
    </Card>
  );
};

export default ArticleDetailPage;
