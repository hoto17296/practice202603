import { Button, Form, Input, Alert } from "antd";
import { useState, type FC } from "react";
import { useNavigate } from "react-router";

import api from "../lib/api";
import { useSession } from "../lib/auth";

interface ArticleNewPageProps {}

const ArticleNewPage: FC<ArticleNewPageProps> = () => {
  useSession();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function onFinish({ title, body }: { title: string; body: string }) {
    setErrorMessage(null);
    setLoading(true);
    const { response, error } = await api.POST("/api/articles/", {
      body: { title, body },
    });
    setLoading(false);
    if (response.ok) {
      navigate("/");
      return;
    }
    if (response.status === 400) {
      if (error?.detail === "TITLE_IS_REQUIRED") setErrorMessage("タイトルを入力してください。");
      else if (error?.detail === "BODY_IS_REQUIRED") setErrorMessage("本文を入力してください。");
      return;
    }
    throw error;
  }

  return (
    <>
      <h2>記事を新規作成</h2>
      <Form layout="vertical" onFinish={onFinish} disabled={loading}>
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
          <Button type="primary" htmlType="submit" loading={loading}>
            投稿する
          </Button>
        </Form.Item>

        {errorMessage ? <Alert message={errorMessage} type="error" showIcon /> : null}
      </Form>
    </>
  );
};

export default ArticleNewPage;
