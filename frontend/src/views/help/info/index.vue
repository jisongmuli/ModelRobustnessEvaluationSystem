<template>
  <div class="app-container">
    <el-card>
      <template slot="header">
        <div class="card-header">
          <span>系统介绍</span>
        </div>
      </template>

      <div class="system-info">
        <h2>模型鲁棒性测试平台</h2>
        <h3>Version 2.0</h3>

        <div class="section">
          <h4>📌 项目简介</h4>
          <p>本系统是一个基于人工智能的模型鲁棒性测试平台，集成了模型上传、对抗攻击测试和结果分析功能。</p>
        </div>

        <div class="section">
          <h4>🛠️ 技术栈</h4>
          <ul class="tech-stack">
            <li><strong>前端框架</strong>  Vue.js 3 / Element UI</li>
            <li><strong>后端框架</strong>  FastAPI (Python)</li>
            <li><strong>模型加载</strong>  PyTorch</li>
            <li><strong>对抗攻击</strong>  FGSM、PGD、BIM、C&W、DeepFool</li>
            <li><strong>数据存储</strong>  MYSQL / 本地文件系统</li>
          </ul>
        </div>

        <div class="section">
          <h4>✨ 功能特性</h4>
          <ul class="features">
            <li>📁 模型文件上传与管理</li>
            <li>🔍 多种对抗攻击方法测试</li>
            <li>📊 详细的测试结果分析</li>
            <li>📋 任务列表与历史记录</li>
            <li>👤 用户注册与个人信息管理</li>
            <li>🖼️ 头像上传与个人化设置</li>
          </ul>
        </div>

        <div class="section">
          <h4>🎯 核心优势</h4>
          <div class="advantages">
            <div class="advantage-item">
              <div class="advantage-icon">🔒</div>
              <h5>安全可靠</h5>
              <p>所有数据在本地处理，不上传服务器，保护用户隐私</p>
            </div>
            <div class="advantage-item">
              <div class="advantage-icon">⚡</div>
              <h5>高效测试</h5>
              <p>多线程并行处理，快速完成对抗攻击测试</p>
            </div>
            <div class="advantage-item">
              <div class="advantage-icon">📊</div>
              <h5>详细分析</h5>
              <p>提供全面的测试结果分析和可视化报告</p>
            </div>
            <div class="advantage-item">
              <div class="advantage-icon">🔧</div>
              <h5>易于使用</h5>
              <p>直观的用户界面，简单几步即可完成测试</p>
            </div>
          </div>
        </div>

        <div class="section">
          <h4>📁 支持的模型格式</h4>
          <div class="model-formats">
            <span class="format-tag">.pt</span>
            <span class="format-tag">.pth</span>
            <span class="format-tag">.onnx</span>
            <span class="format-tag">TorchScript</span>
          </div>
        </div>

        <div class="section">
          <h4>🎨 支持的攻击方法</h4>
          <div class="attack-methods">
            <div class="method-item">
              <span class="method-name">FGSM</span>
              <span class="method-desc">快速梯度符号法</span>
            </div>
            <div class="method-item">
              <span class="method-name">PGD</span>
              <span class="method-desc">投影梯度下降</span>
            </div>
            <div class="method-item">
              <span class="method-name">BIM</span>
              <span class="method-desc">基本迭代法</span>
            </div>
            <div class="method-item">
              <span class="method-name">C&W</span>
              <span class="method-desc">Carlini & Wagner</span>
            </div>
            <div class="method-item">
              <span class="method-name">DeepFool</span>
              <span class="method-desc">最小扰动攻击</span>
            </div>
          </div>
        </div>

        <div class="section">
          <h4>© 2026 模型鲁棒性测试平台 | 仅供学习交流使用</h4>
          <p class="copyright">本系统仅用于演示，所有数据在本地处理，不上传服务器 | 如持续困扰请寻求专业帮助</p>
        </div>
      </div>
    </el-card>

    <el-card class="mt-4 contact-card">
      <template slot="header">
        <div class="card-header">
          <span>联系我们</span>
        </div>
      </template>

      <div class="contact-container">
        <!-- 西安邮电大学 -->
        <div class="contact-card-item">
          <div class="contact-icon">🏫</div>
          <h4>西安邮电大学</h4>
          <div class="contact-details">
            <p class="contact-item">
              <i class="el-icon-position"></i>
              <span>陕西省西安市长安区西长安街563号</span>
            </p>
            <p class="contact-item">
              <i class="el-icon-postcard"></i>
              <span>邮编：710121</span>
            </p>
          </div>
        </div>

        <!-- 作者信息 -->
        <div class="contact-card-item">
          <div class="contact-icon">👨‍💻</div>
          <h4>作者信息</h4>
          <div class="contact-details">
            <p class="contact-item">
              <i class="el-icon-user"></i>
              <span>姓名：李阳</span>
            </p>
            <p class="contact-item">
              <i class="el-icon-message"></i>
              <span>邮箱：3340418738@qq.com</span>
            </p>
            <p class="contact-item">
              <i class="el-icon-phone"></i>
              <span>电话：15877403813</span>
            </p>
          </div>
        </div>

        <!-- 友情链接 -->
        <div class="contact-card-item">
          <div class="contact-icon">🔗</div>
          <h4>友情链接</h4>
          <div class="contact-details links-container">
            <a href="https://www.xiyou.edu.cn/" target="_blank" class="link-item">
              <i class="el-icon-link"></i>
              <span>西安邮电大学官网</span>
            </a>
            <a href="http://cs.xupt.edu.cn:81/xiyoucs/showarticle.asp?ArticleID=3690" target="_blank" class="link-item">
              <i class="el-icon-link"></i>
              <span>西安邮电大学计算机学院</span>
            </a>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: "SystemInfo"
}
</script>

<style scoped>
.app-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.system-info {
  line-height: 1.6;
  text-align: center;
}

.system-info h2 {
  color: #409EFF;
  margin-bottom: 10px;
  font-size: 28px;
  font-weight: 600;
}

.system-info h3 {
  color: #606266;
  margin-bottom: 40px;
  font-size: 18px;
}

.section {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid #e4e7ed;
  text-align: left;
}

.section:last-child {
  border-bottom: none;
}

.section h4 {
  color: #303133;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.tech-stack,
.features {
  list-style: none;
  padding-left: 0;
}

.tech-stack li,
.features li {
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.tech-stack li:before,
.features li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #409EFF;
  font-weight: bold;
}

/* 核心优势 */
.advantages {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.advantage-item {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  padding: 25px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.advantage-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.advantage-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.advantage-item h5 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 600;
}

.advantage-item p {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

/* 模型格式 */
.model-formats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.format-tag {
  background: #ecf5ff;
  color: #409EFF;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #d9ecff;
  transition: all 0.3s ease;
}

.format-tag:hover {
  background: #409EFF;
  color: white;
  transform: scale(1.05);
}

/* 攻击方法 */
.attack-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.method-item {
  background: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.method-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.method-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
  font-size: 15px;
}

.method-desc {
  font-size: 13px;
  color: #909399;
}

.copyright {
  font-size: 14px;
  color: #909399;
  text-align: center;
  margin-top: 20px;
}

.mt-4 {
  margin-top: 30px;
}

/* 联系我们 */
.contact-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.contact-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 20px;
}

.contact-card-item {
  background: white;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.contact-card-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  border-color: #409EFF;
}

.contact-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.contact-card-item h4 {
  color: #303133;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.contact-details {
  text-align: left;
}

.contact-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}

.contact-item i {
  color: #409EFF;
  margin-right: 10px;
  font-size: 16px;
}

.links-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.link-item {
  display: flex;
  align-items: center;
  color: #409EFF;
  text-decoration: none;
  padding: 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.link-item:hover {
  background: #ecf5ff;
  transform: translateX(5px);
}

.link-item i {
  margin-right: 10px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .app-container {
    padding: 15px;
  }

  .system-info h2 {
    font-size: 24px;
  }

  .advantages {
    grid-template-columns: 1fr;
  }

  .contact-container {
    grid-template-columns: 1fr;
  }

  .attack-methods {
    grid-template-columns: 1fr;
  }
}
</style>
