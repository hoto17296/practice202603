import { LockOutlined, MailOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Button, Form, Input } from "antd";
import { useSetAtom } from "jotai";
import { useState, type FC } from "react";

import { authSessionAtom } from "../atoms";
import api from "../lib/api";

interface SignupPageProps {}

const SignupPage: FC<SignupPageProps> = () => {
  const refreshSession = useSetAtom(authSessionAtom);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function onFinish({ email, password, name }: any) {
    setErrorMessage(null);
    setLoading(true);
    const { response, error } = await api.POST("/api/auth/signup", {
      body: { email, password, name },
    });
    setLoading(false);
    if (response.ok) {
      refreshSession();
      return;
    }
    if (response.status === 409) {
      setErrorMessage("そのメールアドレスは既に登録されています。");
      return;
    }
    if (response.status === 400) {
      if (error?.detail === "INVALID_EMAIL_ADDRESS") setErrorMessage("不正なメールアドレスです。");
      else if (error?.detail === "INVALID_PASSWORD")
        setErrorMessage(
          "パスワードは8文字以上で指定してください。使用可能な文字は半角英数字と特殊文字 .!@*_- です。",
        );
      return;
    }
    throw error;
  }

  return (
    <>
      <h2>アカウント登録</h2>
      <Form layout="vertical" autoComplete="off" onFinish={onFinish} disabled={loading}>
        <Form.Item hasFeedback label="Email" name="email" rules={[{ required: true }]}>
          <Input prefix={<MailOutlined />} />
        </Form.Item>

        <Form.Item hasFeedback label="Password" name="password" rules={[{ required: true }]}>
          <Input type="password" prefix={<LockOutlined />} />
        </Form.Item>

        <Form.Item hasFeedback label="Name" name="name" rules={[{ required: true }]}>
          <Input prefix={<UserOutlined />} />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit">
            登録
          </Button>
        </Form.Item>

        {errorMessage ? <Alert message={errorMessage} type="error" showIcon /> : null}
      </Form>
    </>
  );
};

export default SignupPage;
