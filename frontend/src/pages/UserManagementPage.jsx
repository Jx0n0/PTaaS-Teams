import { Button, Card, Form, Input, Modal, Space, Table, Tag, message } from 'antd'
import { useEffect, useState } from 'react'
import { createUser, fetchUsers } from '../api/platform'

export function UserManagementPage() {
  const [users, setUsers] = useState([])
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const load = async () => {
    const { data } = await fetchUsers()
    setUsers(data)
  }

  useEffect(() => { load() }, [])

  const onCreate = async () => {
    const values = await form.validateFields()
    await createUser(values)
    message.success('用户创建成功')
    setOpen(false)
    form.resetFields()
    load()
  }

  return (
    <Card title="用户管理" extra={<Button type="primary" onClick={() => setOpen(true)}>新建用户</Button>}>
      <Table rowKey="id" dataSource={users} pagination={false} columns={[
        { title: 'ID', dataIndex: 'id', width: 80 },
        { title: '用户名', dataIndex: 'username' },
        { title: '邮箱', dataIndex: 'email' },
        { title: '姓名', dataIndex: 'full_name' },
        { title: '角色', dataIndex: 'roles', render: (roles = []) => <Space>{roles.map((r) => <Tag key={r}>{r}</Tag>)}</Space> },
        { title: '状态', dataIndex: 'is_active', render: (v) => v ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag> }
      ]} />

      <Modal title="新建用户" open={open} onOk={onCreate} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email' }]}><Input /></Form.Item>
          <Form.Item name="full_name" label="姓名"><Input /></Form.Item>
          <Form.Item name="password" label="初始密码" rules={[{ required: true }]}><Input.Password /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
