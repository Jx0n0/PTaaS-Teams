import { Button, Card, Form, Modal, Select, Table, Tag, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { createUserRole, fetchRoles, fetchUserRoles, fetchUsers } from '../api/platform'

export function UserRoleBindingPage() {
  const [items, setItems] = useState([])
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const usersMap = useMemo(() => Object.fromEntries(users.map((x) => [x.id, x.username])), [users])
  const rolesMap = useMemo(() => Object.fromEntries(roles.map((x) => [x.id, x.code])), [roles])

  const load = async () => {
    const [ur, u, r] = await Promise.all([fetchUserRoles(), fetchUsers(), fetchRoles()])
    setItems(ur.data)
    setUsers(u.data)
    setRoles(r.data)
  }

  useEffect(() => { load() }, [])

  const onCreate = async () => {
    const values = await form.validateFields()
    await createUserRole(values)
    message.success('用户角色绑定成功')
    setOpen(false)
    form.resetFields()
    load()
  }

  return (
    <Card title="用户角色绑定" extra={<Button type="primary" onClick={() => setOpen(true)}>新增绑定</Button>}>
      <Table rowKey="id" dataSource={items} pagination={false} columns={[
        { title: 'ID', dataIndex: 'id', width: 80 },
        { title: '用户', dataIndex: 'user', render: (v) => usersMap[v] || v },
        { title: '角色', dataIndex: 'role', render: (v) => <Tag>{rolesMap[v] || v}</Tag> },
        { title: '范围', dataIndex: 'scope_type' }
      ]} />

      <Modal title="新增绑定" open={open} onOk={onCreate} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical" initialValues={{ scope_type: 'GLOBAL' }}>
          <Form.Item name="user" label="用户" rules={[{ required: true }]}>
            <Select options={users.map((x) => ({ value: x.id, label: x.username }))} />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Select options={roles.map((x) => ({ value: x.id, label: x.code }))} />
          </Form.Item>
          <Form.Item name="scope_type" label="范围" rules={[{ required: true }]}>
            <Select options={[{ value: 'GLOBAL' }, { value: 'CUSTOMER' }, { value: 'PROJECT' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
