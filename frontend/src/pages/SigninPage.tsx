import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { Alert, Button, Form, Input } from "antd";
import { useSetAtom } from "jotai";
import { useState, type FC } from "react";

import { authSessionAtom } from "../atoms";
import api from "../lib/api";

interface SigninPageProps {}

const SigninPage: FC<SigninPageProps> = () => {
  const refreshSession = useSetAtom(authSessionAtom);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function onFinish({ email, password }: any) {
    setErrorMessage(null);
    setLoading(true);
    const { response, error } = await api.POST("/api/auth/signin", {
      body: { email: email || "", password: password || "" },
    });
    setLoading(false);
    if (response.ok) {
      refreshSession();
      return;
    }
    if (response.status === 400) {
      setErrorMessage("サインインに失敗しました。");
      return;
    }
    throw error;
  }

  return (
    <>
      <h2>サインイン</h2>
      <Form layout="vertical" autoComplete="off" onFinish={onFinish} disabled={loading}>
        <Form.Item hasFeedback label="Email" name="email" validateDebounce={400}>
          <Input prefix={<MailOutlined />} />
        </Form.Item>

        <Form.Item hasFeedback label="Password" name="password" validateDebounce={400}>
          <Input type="password" prefix={<LockOutlined />} />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit">
            サインイン
          </Button>
        </Form.Item>

        {errorMessage ? <Alert title={errorMessage} type="error" showIcon /> : null}
      </Form>
    </>
  );
};

export default SigninPage;
