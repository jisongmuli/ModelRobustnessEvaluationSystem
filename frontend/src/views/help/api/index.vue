<template>
  <div class="system-info-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">API文档</h1>
      <p class="page-subtitle">系统接口详细说明与使用指南</p>
    </div>

    <!-- 核心内容区 -->
    <div class="content-section">
      <!-- API 概览 -->
      <div class="info-card">
        <h2 class="section-title">API 概览</h2>
        <div class="section-content">
          <p>本系统提供了完整的 RESTful API 接口，支持用户认证、模型管理、攻击测试等功能。所有接口均需要在请求头中携带有效的 JWT token 进行身份验证。</p>
          <div class="api-overview">
            <div class="api-stat">
              <div class="stat-number">40+</div>
              <div class="stat-label">API 接口</div>
            </div>
            <div class="api-stat">
              <div class="stat-number">5</div>
              <div class="stat-label">功能模块</div>
            </div>
            <div class="api-stat">
              <div class="stat-number">24/7</div>
              <div class="stat-label">服务可用性</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 认证 API -->
      <div class="info-card">
        <h2 class="section-title">认证 API</h2>
        <div class="api-list">
          <!-- 登录接口 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method post">POST</span>
              <span class="api-path">/api/login</span>
              <span class="api-title">用户登录</span>
            </div>
            <div class="api-details">
              <h3>请求参数</h3>
              <pre class="code-block">{
  "username": "string",  // 用户名
  "password": "string",  // 密码
  "code": "string",      // 验证码（可选）
  "uuid": "string"       // 验证码UUID（可选）
}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "登录成功",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}</pre>
            </div>
          </div>

          <!-- 注册接口 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method post">POST</span>
              <span class="api-path">/api/register</span>
              <span class="api-title">用户注册</span>
            </div>
            <div class="api-details">
              <h3>请求参数</h3>
              <pre class="code-block">{
  "username": "string",      // 用户名
  "password": "string",      // 密码
  "confirmPassword": "string", // 确认密码
  "nickName": "string",      // 昵称（可选）
  "email": "string",         // 邮箱（可选）
  "phonenumber": "string"    // 手机号（可选）
}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "userId": 1,
    "userName": "test",
    "nickName": "测试用户"
  }
}</pre>
            </div>
          </div>

          <!-- 获取用户信息 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method get">GET</span>
              <span class="api-path">/api/getInfo</span>
              <span class="api-title">获取用户信息</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "操作成功",
  "user": {
    "userId": 1,
    "userName": "test",
    "nickName": "测试用户",
    "avatar": "",
    "admin": false
  },
  "roles": ["common"],
  "permissions": ["system:user:list"]
}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 模型管理 API -->
      <div class="info-card">
        <h2 class="section-title">模型管理 API</h2>
        <div class="api-list">
          <!-- 上传模型 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method post">POST</span>
              <span class="api-path">/api/model/upload</span>
              <span class="api-title">上传模型</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}
Content-Type: multipart/form-data</pre>
              <h3>请求参数</h3>
              <pre class="code-block">model_file: 文件       // 模型文件
model_name: string     // 模型名称
description: string    // 模型描述（可选）
model_type: string     // 模型类型</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "model_id": 1,
    "model_name": "ResNet50",
    "file_path": "/uploads/models/model.pth"
  }
}</pre>
            </div>
          </div>

          <!-- 获取模型列表 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method get">GET</span>
              <span class="api-path">/api/model/list</span>
              <span class="api-title">获取模型列表</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "model_id": 1,
      "model_name": "ResNet50",
      "description": "ResNet50 图像分类模型",
      "model_type": "image_classification",
      "create_time": "2026-03-12T00:00:00"
    }
  ]
}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 攻击测试 API -->
      <div class="info-card">
        <h2 class="section-title">攻击测试 API</h2>
        <div class="api-list">
          <!-- 创建攻击任务 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method post">POST</span>
              <span class="api-path">/api/attack/create</span>
              <span class="api-title">创建攻击任务</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}
Content-Type: application/json</pre>
              <h3>请求参数</h3>
              <pre class="code-block">{
  "model_id": 1,           // 模型ID
  "attack_method": "fgsm",  // 攻击方法
  "epsilon": 0.03,          // 扰动大小
  "iterations": 10,         // 迭代次数（可选）
  "dataset_id": 1           // 数据集ID
}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "任务创建成功",
  "data": {
    "task_id": 1,
    "status": "pending"
  }
}</pre>
            </div>
          </div>

          <!-- 获取任务结果 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method get">GET</span>
              <span class="api-path">/api/attack/result/{taskId}</span>
              <span class="api-title">获取任务结果</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "task_id": 1,
    "model_name": "ResNet50",
    "attack_method": "fgsm",
    "original_accuracy": 0.95,
    "adversarial_accuracy": 0.32,
    "robustness_score": 0.34
  }
}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 个人信息 API -->
      <div class="info-card">
        <h2 class="section-title">个人信息 API</h2>
        <div class="api-list">
          <!-- 获取个人信息 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method get">GET</span>
              <span class="api-path">/api/system/user/profile</span>
              <span class="api-title">获取个人信息</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "userId": 1,
    "userName": "test",
    "nickName": "测试用户",
    "phonenumber": "",
    "email": "",
    "sex": "0",
    "avatar": "",
    "createTime": "2026-03-12T00:00:00"
  },
  "roleGroup": "普通用户",
  "postGroup": ""
}</pre>
            </div>
          </div>

          <!-- 上传头像 -->
          <div class="api-item">
            <div class="api-header">
              <span class="api-method post">POST</span>
              <span class="api-path">/api/system/user/profile/avatar</span>
              <span class="api-title">上传头像</span>
            </div>
            <div class="api-details">
              <h3>请求头</h3>
              <pre class="code-block">Authorization: Bearer {token}
Content-Type: multipart/form-data</pre>
              <h3>请求参数</h3>
              <pre class="code-block">avatar: 文件       // 头像文件</pre>
              <h3>响应示例</h3>
              <pre class="code-block">{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "imgUrl": "/uploads/avatars/avatar.jpg"
  }
}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系我们 -->
    <div class="contact-section">
      <h2 class="section-title">联系我们</h2>
      <div class="contact-content">
        <div class="contact-info">
          <p><i class="el-icon-location"></i> 西安邮电大学</p>
          <p><i class="el-icon-user"></i> 作者：李阳</p>
          <p><i class="el-icon-message"></i> 邮箱：3340418738@qq.com</p>
          <p><i class="el-icon-phone"></i> 电话：15877403813</p>
        </div>
        <div class="friend-links">
          <h3>友情链接</h3>
          <ul>
            <li><a href="https://www.xiyou.edu.cn/" target="_blank">西安邮电大学官网</a></li>
            <li><a href="http://cs.xupt.edu.cn:81/xiyoucs/showarticle.asp?ArticleID=3690" target="_blank">西安邮电大学计算机学院官网</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ApiDoc',
  data() {
    return {}
  }
}
</script>

<style scoped>
.system-info-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  color: #333;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  color: white;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.page-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

.content-section {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #667eea;
  border-bottom: 3px solid #667eea;
  padding-bottom: 0.5rem;
  display: inline-block;
}

/* API 概览样式 */
.api-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.api-stat {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
}

/* API 列表样式 */
.api-list {
  margin-top: 1.5rem;
}

.api-item {
  margin-bottom: 2rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.api-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);
}

.api-header {
  background: #f8f9fa;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.api-method {
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
  color: white;
}

.api-method.get {
  background: #4CAF50;
}

.api-method.post {
  background: #2196F3;
}

.api-method.put {
  background: #FF9800;
}

.api-method.delete {
  background: #F44336;
}

.api-path {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.api-title {
  font-weight: bold;
  color: #667eea;
}

.api-details {
  padding: 1.5rem;
}

.api-details h3 {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.8rem;
  color: #333;
}

.code-block {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.4;
  overflow-x: auto;
  margin-bottom: 1rem;
  border-left: 4px solid #667eea;
}

/* 联系我们样式 */
.contact-section {
  max-width: 1200px;
  margin: 3rem auto 0;
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.contact-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.contact-info p {
  margin-bottom: 0.8rem;
  display: flex;
  align-items: center;
  color: #666;
}

.contact-info i {
  margin-right: 0.8rem;
  color: #667eea;
  font-size: 1.2rem;
}

.friend-links h3 {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #333;
}

.friend-links ul {
  list-style: none;
  padding: 0;
}

.friend-links li {
  margin-bottom: 0.8rem;
}

.friend-links a {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
  display: inline-block;
  position: relative;
}

.friend-links a:hover {
  color: #764ba2;
}

.friend-links a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: #764ba2;
  transition: width 0.3s ease;
}

.friend-links a:hover::after {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .system-info-container {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .info-card {
    padding: 1.5rem;
  }

  .contact-content {
    grid-template-columns: 1fr;
  }

  .api-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .api-path {
    width: 100%;
  }
}
</style>
