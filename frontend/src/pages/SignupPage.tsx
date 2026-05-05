import { LockOutlined, MailOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Button, Form, Input } from "antd";
import { useAtomValue } from "jotai";
import { useState, type FC } from "react";
import { Link, Navigate, useNavigate } from "react-router";

import { authSessionAtom } from "../atoms";
import api from "../lib/api";

interface SignupPageProps {}

const SignupPage: FC<SignupPageProps> = () => {
  const session = useAtomValue(authSessionAtom);
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (session) return <Navigate to="/" replace />;

  async function onFinish({ email, password, name }: any) {
    setErrorMessage(null);
    setLoading(true);
    const { response, error } = await api.POST("/api/auth/signup", {
      body: { email, password, name },
    });
    setLoading(false);
    if (response.ok) {
      navigate("/");
      return;
    }
    // TODO: i18n
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
      <h2>Sign up</h2>
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
            Sign up
          </Button>
        </Form.Item>

        {errorMessage ? <Alert message={errorMessage} type="error" showIcon /> : null}
      </Form>
    </>
  );
};

export default SignupPage;
