import { Button, Card, Form, Input, Space, Typography, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { login } from '../api/auth'
import { setTokens } from '../api/client'

const { Title, Text } = Typography

export function LoginPage({ onLogin }) {
  const [form] = Form.useForm()

  const onFinish = async (values) => {
    try {
      const { data } = await login(values)
      setTokens(data.access, data.refresh)
      message.success('登录成功')
      onLogin(data.user)
    } catch (e) {
      message.error(e.response?.data?.detail || '登录失败，请检查账号密码')
    }
  }

  return (
    <div className="login-wrap">
      <Card className="login-card" bordered={false}>
        <Space direction="vertical" size={2} style={{ marginBottom: 24 }}>
          <Title level={3} style={{ marginBottom: 0 }}>PTaaS Teams 控制台</Title>
          <Text type="secondary">内部渗透测试协作与交付平台</Text>
        </Space>

        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block size="large">
            登录
          </Button>
        </Form>
      </Card>
    </div>
  )
}
