<template>
  <div class="system-info-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">操作指南</h1>
      <p class="page-subtitle">详细的系统操作步骤和使用说明</p>
    </div>

    <!-- 核心内容区 -->
    <div class="content-section">
      <!-- 快速开始 -->
      <div class="info-card">
        <h2 class="section-title">快速开始</h2>
        <div class="section-content">
          <ol class="step-list">
            <li class="step-item">
              <div class="step-number">1</div>
              <div class="step-content">
                <h3>注册/登录系统</h3>
                <p>点击顶部导航栏的「注册」按钮创建新账号，或使用已有账号登录系统。</p>
              </div>
            </li>
            <li class="step-item">
              <div class="step-number">2</div>
              <div class="step-content">
                <h3>上传模型</h3>
                <p>进入「鲁棒性测试」→「模型管理」页面，点击「上传模型」按钮，选择模型文件并填写相关信息。</p>
              </div>
            </li>
            <li class="step-item">
              <div class="step-number">3</div>
              <div class="step-content">
                <h3>创建测试任务</h3>
                <p>进入「鲁棒性测试」→「攻击测试」页面，选择已上传的模型，配置攻击参数，点击「开始测试」。</p>
              </div>
            </li>
            <li class="step-item">
              <div class="step-number">4</div>
              <div class="step-content">
                <h3>查看测试结果</h3>
                <p>进入「鲁棒性测试」→「任务列表」页面，点击「查看结果」按钮查看详细的测试报告。</p>
              </div>
            </li>
          </ol>
        </div>
      </div>

      <!-- 功能模块使用说明 -->
      <div class="info-card">
        <h2 class="section-title">功能模块使用说明</h2>

        <!-- 模型管理 -->
        <div class="module-info">
          <h3>1. 模型管理</h3>
          <p><strong>功能说明：</strong>用于上传、管理和删除测试模型。</p>
          <p><strong>操作步骤：</strong></p>
          <ul>
            <li>点击「上传模型」按钮</li>
            <li>选择模型文件（支持 .pt、.pth 格式）</li>
            <li>填写模型名称、描述等信息</li>
            <li>点击「确认上传」完成操作</li>
          </ul>
        </div>

        <!-- 攻击测试 -->
        <div class="module-info">
          <h3>2. 攻击测试</h3>
          <p><strong>功能说明：</strong>对模型进行各种对抗攻击测试，评估模型鲁棒性。</p>
          <p><strong>操作步骤：</strong></p>
          <ul>
            <li>选择目标模型</li>
            <li>选择攻击方法（FGSM、PGD等）</li>
            <li>配置攻击参数（扰动大小、迭代次数等）</li>
            <li>选择测试数据集</li>
            <li>点击「开始测试」启动测试任务</li>
          </ul>
        </div>

        <!-- 任务列表 -->
        <div class="module-info">
          <h3>3. 任务列表</h3>
          <p><strong>功能说明：</strong>查看和管理所有测试任务。</p>
          <p><strong>操作步骤：</strong></p>
          <ul>
            <li>查看任务状态和基本信息</li>
            <li>点击「查看结果」查看详细测试报告</li>
            <li>点击「删除」移除已完成的任务</li>
            <li>使用搜索和筛选功能快速找到特定任务</li>
          </ul>
        </div>

        <!-- 个人中心 -->
        <div class="module-info">
          <h3>4. 个人中心</h3>
          <p><strong>功能说明：</strong>管理个人信息和账户设置。</p>
          <p><strong>操作步骤：</strong></p>
          <ul>
            <li>点击右上角用户头像，选择「个人中心」</li>
            <li>修改个人基本信息</li>
            <li>上传个人头像</li>
            <li>修改登录密码</li>
          </ul>
        </div>
      </div>

      <!-- 常见操作技巧 -->
      <div class="info-card">
        <h2 class="section-title">操作技巧</h2>
        <div class="tips-list">
          <div class="tip-item">
            <h3>批量操作</h3>
            <p>在任务列表页面，可勾选多个任务进行批量删除操作。</p>
          </div>
          <div class="tip-item">
            <h3>快速导航</h3>
            <p>使用左侧菜单栏快速切换不同功能模块。</p>
          </div>
          <div class="tip-item">
            <h3>结果导出</h3>
            <p>测试结果页面支持导出详细报告，方便后续分析。</p>
          </div>
          <div class="tip-item">
            <h3>快捷键</h3>
            <p>使用 Ctrl+K 快速打开搜索功能，提高操作效率。</p>
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
  name: 'OperationGuide',
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

/* 步骤列表样式 */
.step-list {
  list-style: none;
  padding: 0;
}

.step-item {
  display: flex;
  margin-bottom: 2rem;
  position: relative;
}

.step-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 25px;
  top: 50px;
  bottom: -30px;
  width: 2px;
  background: #e0e0e0;
}

.step-number {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
  flex-shrink: 0;
  margin-right: 1.5rem;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #333;
}

.step-content p {
  color: #666;
  line-height: 1.6;
}

/* 模块信息样式 */
.module-info {
  margin-bottom: 2rem;
  padding-left: 1.5rem;
  border-left: 4px solid #667eea;
}

.module-info h3 {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 0.8rem;
  color: #333;
}

.module-info p {
  margin-bottom: 0.5rem;
  color: #666;
}

.module-info ul {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.module-info li {
  margin-bottom: 0.3rem;
  color: #666;
}

/* 技巧列表样式 */
.tips-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.tip-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #764ba2;
}

.tip-item h3 {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #333;
}

.tip-item p {
  color: #666;
  line-height: 1.5;
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

  .step-item {
    flex-direction: column;
  }

  .step-number {
    margin-bottom: 1rem;
  }

  .step-item:not(:last-child)::before {
    left: 25px;
    top: 70px;
  }
}
</style>
