import { Button, Card, Form, Input, message } from 'antd'
import { changePassword } from '../api/auth'

export function AccountSecurityPage() {
  const [form] = Form.useForm()

  const onSubmit = async () => {
    const values = await form.validateFields()
    await changePassword(values)
    message.success('密码修改成功')
    form.resetFields()
  }

  return (
    <Card title="账户安全 / 修改密码">
      <Form form={form} layout="vertical" style={{ maxWidth: 480 }}>
        <Form.Item name="old_password" label="旧密码" rules={[{ required: true }]}><Input.Password /></Form.Item>
        <Form.Item name="new_password" label="新密码" rules={[{ required: true }]}><Input.Password /></Form.Item>
        <Form.Item
          name="new_password_confirm"
          label="确认新密码"
          rules={[
            { required: true },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('new_password') === value) return Promise.resolve()
                return Promise.reject(new Error('两次输入的密码不一致'))
              }
            })
          ]}
        ><Input.Password /></Form.Item>
        <Button type="primary" onClick={onSubmit}>更新密码</Button>
      </Form>
    </Card>
  )
}
