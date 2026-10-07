<template>
  <div class="system-info-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">常见问题解答</h1>
      <p class="page-subtitle">系统使用过程中常见问题的详细解答</p>
    </div>

    <!-- 核心内容区 -->
    <div class="content-section">
      <!-- 常见问题列表 -->
      <div class="info-card">
        <h2 class="section-title">常见问题</h2>
        <div class="faq-list">
          <!-- 登录注册相关 -->
          <div class="faq-category">
            <h3 class="category-title">登录注册</h3>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(1)">
                <span class="question-text">如何注册新账号？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 1 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 1">
                <p>点击系统登录页面的「注册」按钮，填写用户名、密码、确认密码等信息，点击「注册」按钮即可完成账号创建。注册成功后，系统会自动跳转到登录页面。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(2)">
                <span class="question-text">忘记密码怎么办？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 2 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 2">
                <p>目前系统暂不支持密码找回功能。如果您忘记了密码，请联系系统管理员重置密码。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(3)">
                <span class="question-text">注册时显示「用户名已存在」怎么办？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 3 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 3">
                <p>如果显示「用户名已存在」，说明该用户名已经被其他用户注册。请尝试使用其他用户名进行注册。</p>
              </div>
            </div>
          </div>

          <!-- 模型管理相关 -->
          <div class="faq-category">
            <h3 class="category-title">模型管理</h3>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(4)">
                <span class="question-text">支持哪些格式的模型文件？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 4 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 4">
                <p>系统支持 PyTorch 模型文件，包括 .pt 和 .pth 格式。请确保模型文件是有效的 PyTorch 模型，并且包含完整的模型结构和权重。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(5)">
                <span class="question-text">上传模型失败怎么办？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 5 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 5">
                <p>上传模型失败可能的原因包括：</p>
                <ul>
                  <li>文件大小超过限制（最大支持 100MB）</li>
                  <li>文件格式不正确</li>
                  <li>模型文件损坏</li>
                  <li>网络连接问题</li>
                </ul>
                <p>请检查以上问题后重新尝试上传。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(6)">
                <span class="question-text">如何删除已上传的模型？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 6 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 6">
                <p>在模型管理页面，找到需要删除的模型，点击操作列中的「删除」按钮，确认删除操作即可。删除后，模型文件将被永久移除，无法恢复。</p>
              </div>
            </div>
          </div>

          <!-- 攻击测试相关 -->
          <div class="faq-category">
            <h3 class="category-title">攻击测试</h3>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(7)">
                <span class="question-text">支持哪些攻击方法？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 7 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 7">
                <p>系统支持多种对抗攻击方法，包括：</p>
                <ul>
                  <li>FGSM (Fast Gradient Sign Method)</li>
                  <li>PGD (Projected Gradient Descent)</li>
                  <li>CW (Carlini & Wagner)</li>
                  <li>DeepFool</li>
                  <li>JSMA (Jacobian-based Saliency Map Attack)</li>
                </ul>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(8)">
                <span class="question-text">测试任务执行时间过长怎么办？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 8 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 8">
                <p>测试任务的执行时间取决于模型大小、数据集规模和攻击方法的复杂度。对于大型模型和复杂攻击，可能需要较长时间。您可以：</p>
                <ul>
                  <li>使用较小的测试数据集</li>
                  <li>降低攻击的迭代次数</li>
                  <li>选择计算复杂度较低的攻击方法</li>
                </ul>
                <p>系统会在后台继续执行任务，您可以关闭浏览器窗口，稍后再查看结果。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(9)">
                <span class="question-text">测试结果如何解读？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 9 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 9">
                <p>测试结果包含以下指标：</p>
                <ul>
                  <li><strong>原始准确率：</strong>模型在干净样本上的准确率</li>
                  <li><strong>对抗准确率：</strong>模型在对抗样本上的准确率</li>
                  <li><strong>鲁棒性得分：</strong>对抗准确率与原始准确率的比值，值越高表示模型鲁棒性越好</li>
                  <li><strong>攻击成功率：</strong>攻击成功的样本比例</li>
                </ul>
                <p>您可以通过这些指标评估模型的鲁棒性水平，并与其他模型进行比较。</p>
              </div>
            </div>
          </div>

          <!-- 系统使用相关 -->
          <div class="faq-category">
            <h3 class="category-title">系统使用</h3>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(10)">
                <span class="question-text">如何上传个人头像？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 10 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 10">
                <p>点击右上角用户头像，选择「个人中心」，在个人信息页面点击「上传头像」按钮，选择本地图片文件，点击「确认上传」即可。支持 JPG、PNG 等常见图片格式，文件大小不超过 2MB。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(11)">
                <span class="question-text">不同用户之间是否可以看到彼此的任务？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 11 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 11">
                <p>系统实现了严格的用户数据隔离机制，每个用户只能看到和管理自己的模型、数据集和测试任务。其他用户无法访问您的个人数据，确保数据安全性和隐私保护。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(12)">
                <span class="question-text">系统支持哪些浏览器？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 12 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 12">
                <p>系统支持以下主流浏览器：</p>
                <ul>
                  <li>Google Chrome（推荐，版本 80+）</li>
                  <li>Mozilla Firefox（版本 75+）</li>
                  <li>Microsoft Edge（版本 80+）</li>
                  <li>Safari（版本 13+）</li>
                </ul>
                <p>为了获得最佳使用体验，建议使用 Google Chrome 浏览器。</p>
              </div>
            </div>
            <div class="faq-item">
              <div class="faq-question" @click="toggleFaq(13)">
                <span class="question-text">遇到系统错误怎么办？</span>
                <span class="toggle-icon" :class="{ 'active': openFaq === 13 }">
                  <i class="el-icon-arrow-down"></i>
                </span>
              </div>
              <div class="faq-answer" v-show="openFaq === 13">
                <p>如果遇到系统错误，请尝试以下步骤：</p>
                <ul>
                  <li>刷新页面，重新尝试操作</li>
                  <li>清除浏览器缓存，重新登录系统</li>
                  <li>检查网络连接是否正常</li>
                  <li>如果问题仍然存在，请联系系统管理员或通过页面底部的联系方式寻求帮助</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 联系我们 -->
      <div class="info-card">
        <h2 class="section-title">其他问题</h2>
        <div class="other-questions">
          <p>如果您有其他问题或建议，欢迎通过以下方式联系我们：</p>
          <div class="contact-info">
            <p><i class="el-icon-message"></i> 邮箱：3340418738@qq.com</p>
            <p><i class="el-icon-phone"></i> 电话：15877403813</p>
          </div>
          <p class="response-time">我们会在 1-2 个工作日内回复您的问题。</p>
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
  name: 'Faq',
  data() {
    return {
      openFaq: null
    }
  },
  methods: {
    toggleFaq(id) {
      this.openFaq = this.openFaq === id ? null : id
    }
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

/* FAQ 列表样式 */
.faq-list {
  margin-top: 1.5rem;
}

.faq-category {
  margin-bottom: 2rem;
}

.category-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #333;
  padding-left: 1rem;
  border-left: 4px solid #667eea;
}

.faq-item {
  margin-bottom: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.faq-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.faq-question {
  background: #f8f9fa;
  padding: 1.2rem 1.5rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.3s ease;
}

.faq-question:hover {
  background: #f0f2f5;
}

.question-text {
  font-weight: bold;
  color: #333;
  flex: 1;
}

.toggle-icon {
  transition: transform 0.3s ease;
  color: #667eea;
}

.toggle-icon.active {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 1.5rem;
  background: white;
  border-top: 1px solid #e0e0e0;
  animation: slideDown 0.3s ease;
}

.faq-answer p {
  margin-bottom: 1rem;
  color: #666;
  line-height: 1.6;
}

.faq-answer ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.faq-answer li {
  margin-bottom: 0.5rem;
  color: #666;
}

/* 其他问题样式 */
.other-questions {
  text-align: center;
  padding: 1rem;
}

.other-questions p {
  margin-bottom: 1.5rem;
  color: #666;
  line-height: 1.6;
}

.response-time {
  font-style: italic;
  color: #999;
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

/* 动画效果 */
@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
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

  .faq-question {
    padding: 1rem;
  }

  .faq-answer {
    padding: 1rem;
  }
}
</style>
