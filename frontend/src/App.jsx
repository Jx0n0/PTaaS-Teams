import { LogoutOutlined, SafetyOutlined, TeamOutlined, UserSwitchOutlined } from '@ant-design/icons'
import { Avatar, Button, Layout, Menu, Space, Tag, Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { me } from './api/auth'
import { clearTokens, getAccessToken } from './api/client'
import { LoginPage } from './components/LoginPage'
import { AccountSecurityPage } from './pages/AccountSecurityPage'
import { DashboardPage } from './pages/DashboardPage'
import { RoleManagementPage } from './pages/RoleManagementPage'
import { UserManagementPage } from './pages/UserManagementPage'
import { UserRoleBindingPage } from './pages/UserRoleBindingPage'

const { Header, Sider, Content } = Layout
const { Text } = Typography

export function App() {
  const [collapsed, setCollapsed] = useState(false)
  const [user, setUser] = useState(null)
  const [active, setActive] = useState('dashboard')

  const loadMe = async () => {
    if (!getAccessToken()) return
    try {
      const { data } = await me()
      setUser(data)
    } catch {
      clearTokens()
      setUser(null)
    }
  }

  useEffect(() => { loadMe() }, [])

  const menuItems = useMemo(() => [
    { key: 'dashboard', icon: <SafetyOutlined />, label: '工作台' },
    { key: 'users', icon: <TeamOutlined />, label: '用户管理' },
    { key: 'roles', icon: <UserSwitchOutlined />, label: '角色管理' },
    { key: 'user_roles', icon: <UserSwitchOutlined />, label: '用户角色绑定' },
    { key: 'security', icon: <SafetyOutlined />, label: '账户安全' },
    { key: 'business_placeholder', icon: <SafetyOutlined />, label: '业务模块(Phase2)', disabled: true }
  ], [])

  const renderContent = () => {
    switch (active) {
      case 'users': return <UserManagementPage />
      case 'roles': return <RoleManagementPage />
      case 'user_roles': return <UserRoleBindingPage />
      case 'security': return <AccountSecurityPage />
      default: return <DashboardPage user={user} />
    }
  }

  const logout = () => {
    clearTokens()
    setUser(null)
  }

  if (!user) {
    return <LoginPage onLogin={(u) => setUser(u)} />
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="light">
        <div className="logo">PTaaS</div>
        <Menu mode="inline" selectedKeys={[active]} items={menuItems} onClick={({ key }) => setActive(key)} />
      </Sider>

      <Layout>
        <Header className="header">
          <Space>
            <Avatar>{user.username[0]?.toUpperCase()}</Avatar>
            <Text strong>{user.full_name || user.username}</Text>
            {(user.roles || []).map((r) => <Tag key={r}>{r}</Tag>)}
          </Space>
          <Button icon={<LogoutOutlined />} onClick={logout}>退出登录</Button>
        </Header>

        <Content className="content">{renderContent()}</Content>
      </Layout>
    </Layout>
  )
}
