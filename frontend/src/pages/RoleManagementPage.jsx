import { Button, Card, Form, Input, Modal, Table, message } from 'antd'
import { useEffect, useState } from 'react'
import { createRole, fetchRoles } from '../api/platform'

export function RoleManagementPage() {
  const [roles, setRoles] = useState([])
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const load = async () => {
    const { data } = await fetchRoles()
    setRoles(data)
  }

  useEffect(() => { load() }, [])

  const onCreate = async () => {
    const values = await form.validateFields()
    await createRole(values)
    message.success('角色创建成功')
    setOpen(false)
    form.resetFields()
    load()
  }

  return (
    <Card title="角色管理" extra={<Button type="primary" onClick={() => setOpen(true)}>新建角色</Button>}>
      <Table rowKey="id" dataSource={roles} pagination={false} columns={[
        { title: 'ID', dataIndex: 'id', width: 80 },
        { title: '编码', dataIndex: 'code' },
        { title: '名称', dataIndex: 'name' },
        { title: '描述', dataIndex: 'description' }
      ]} />

      <Modal title="新建角色" open={open} onOk={onCreate} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="code" label="角色编码" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="name" label="角色名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="说明"><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
