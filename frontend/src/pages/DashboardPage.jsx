import { Card, Col, Row, Statistic, Tag, Typography } from 'antd'

const { Title, Text } = Typography

export function DashboardPage({ user }) {
  return (
    <div>
      <Title level={4}>欢迎回来，{user?.full_name || user?.username}</Title>
      <Text type="secondary">当前阶段聚焦平台基础设施：认证、用户、角色、权限边界。</Text>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card><Statistic title="当前登录用户" value={user?.username || '-'} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="角色数" value={user?.roles?.length || 0} /></Card>
        </Col>
        <Col span={8}>
          <Card>
            <div>角色标签</div>
            <div style={{ marginTop: 8 }}>{(user?.roles || []).map((r) => <Tag key={r}>{r}</Tag>)}</div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
