import { Alert, Button, Form, Input, Space } from "antd";
import { useEffect, useState, type FC } from "react";
import { Link, useNavigate, useParams } from "react-router";

import api from "../lib/api";
import { useSession } from "../lib/auth";

interface ArticleEditPageProps {}

const ArticleEditPage: FC<ArticleEditPageProps> = () => {
  const session = useSession();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [forbidden, setForbidden] = useState(false);

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
        if (!data) return;
        if (data.author_id !== session.user.id) {
          setForbidden(true);
          return;
        }
        form.setFieldsValue({ title: data.title, body: data.body });
      });
  }, [id]);

  function handleCancel() {
    if (window.confirm("編集を破棄して記事に戻りますか？")) navigate(`/article/${id}`);
  }

  async function onFinish({ title, body }: { title: string; body: string }) {
    if (!id) return;
    setErrorMessage(null);
    setLoading(true);
    const { response, error } = await api.PATCH("/api/articles/{article_id}", {
      params: { path: { article_id: id } },
      body: { title, body },
    });
    setLoading(false);
    if (response.ok) {
      navigate(`/article/${id}`);
      return;
    }
    if (response.status === 400) {
      if (error?.detail === "TITLE_IS_REQUIRED") setErrorMessage("タイトルを入力してください。");
      else if (error?.detail === "BODY_IS_REQUIRED") setErrorMessage("本文を入力してください。");
      return;
    }
    throw error;
  }

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

  if (forbidden) {
    return (
      <>
        <p>この記事を編集する権限がありません。</p>
        <p>
          <Link to={`/article/${id}`}>記事に戻る</Link>
        </p>
      </>
    );
  }

  return (
    <>
      <h2>記事を編集</h2>
      <Form form={form} layout="vertical" onFinish={onFinish} disabled={loading}>
        <Form.Item
          label="タイトル"
          name="title"
          rules={[{ required: true, message: "タイトルを入力してください。" }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="本文"
          name="body"
          rules={[{ required: true, message: "本文を入力してください。" }]}
        >
          <Input.TextArea rows={10} />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading}>
              保存する
            </Button>
            <Button onClick={handleCancel} disabled={loading}>
              キャンセル
            </Button>
          </Space>
        </Form.Item>

        {errorMessage ? <Alert message={errorMessage} type="error" showIcon /> : null}
      </Form>
    </>
  );
};

export default ArticleEditPage;
