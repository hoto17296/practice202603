import { PlusOutlined } from "@ant-design/icons";
import { Button, Card, Tooltip } from "antd";
import { useEffect, useState, type FC } from "react";
import { useNavigate } from "react-router";

import api, { type ApiSchemaTypes } from "../lib/api";

interface IndexPageProps {}

const IndexPage: FC<IndexPageProps> = () => {
  const navigate = useNavigate();
  const [articles, setArticles] = useState<ApiSchemaTypes["ArticleSummary"][]>([]);

  useEffect(() => {
    api.GET("/api/articles/").then(({ data, error }) => {
      if (error) throw error;
      setArticles(data ?? []);
    });
  }, []);

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h3 style={{ margin: 0 }}>記事一覧</h3>
        <Tooltip title="新しい記事を書く">
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/article/new")} />
        </Tooltip>
      </div>
      {articles.length === 0 ? (
        <p>まだ記事がありません。</p>
      ) : (
        <>
          {articles.map((article) => (
            <Card
              key={article.id}
              hoverable
              onClick={() => navigate(`/article/${article.id}`)}
              style={{ margin: "1em 0" }}
            >
              <Card.Meta
                title={article.title}
                description={
                  <span style={{ color: "var(--color-note)", fontSize: "0.85em" }}>
                    {article.author_name} · {new Date(article.published_at).toLocaleString("ja-JP")}
                  </span>
                }
              />
            </Card>
          ))}
        </>
      )}
    </>
  );
};

export default IndexPage;
